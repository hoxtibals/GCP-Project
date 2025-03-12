#!/bin/bash

PIPE="/tmp/metrics_pipe"
LOG_FILE="/tmp/metrics.log"
PORT=5000

# Create the named pipe
if [[ ! -p $PIPE ]]; then
    mkfifo $PIPE
fi

# what we will use to collect metrics (local use only)
collect_metrics() {
    while true; do
        TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
        CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
        MEM=$(free -m | awk 'NR==2{printf "%s/%s MB (%.2f%%)", $3, $2, $3*100/$2}')
        IO=$(iostat | awk 'NR==4 {print $1}')  
        FS=$(df -h / | awk 'NR==2{print $5}') 
        POWER=$(cat /sys/class/power_supply/BAT0/capacity 2>/dev/null || echo "N/A")

        METRIC="{\"time\": \"$TIMESTAMP\", \"cpu\": \"$CPU%\", \"memory\": \"$MEM\", \"io\": \"$IO\", \"filesystem\": \"$FS\", \"power\": \"$POWER%\"}"
        
        echo "$METRIC" > $PIPE
        echo "$METRIC" >> $LOG_FILE  # Store for history
        
        sleep 15  #HERE WE CAN CHANGE OUR INTERVAL FOR TESTS
    done
}

# Start collecting metrics in background and start logging
collect_metrics &

# API Server
while true; do
#read request using
    nc -l -p $PORT -q 1 | (
        read REQUEST
        
        # Check if request is for history
        if echo "$REQUEST" | grep -q "/history?time="; then
            REQ_TIME=$(echo "$REQUEST" | grep -oP "(?<=/history\?time=)[0-9]{2}:[0-9]{2}")
            # Format today's date for comparison
            TODAY=$(date "+%Y-%m-%d")
            # Get current time minus 1 minute
            CURRENT_TIME=$(date -d "1 minute ago" "+%H:%M") 
            #we would use awk to better handle strings and be able to compare time
            #@note THIS IS ONLY GRABING DATA FROM TODAY
            HIST_DATA=$(awk -v start="$TODAY $REQ_TIME" -v end="$TODAY $CURRENT_TIME" '
        $0 ~ /\"time\"/ {
            #Get the timestamp
            match($0, /"time": "([^"]+)"/, timestamp)
            ts = timestamp[1]
            
            #using awk, we can quickly compare the timestamps
            if (ts >= start && ts <= end) {
                print $0
            }
        }
    ' "$LOG_FILE" | jq -s .)
            
            if [[ -z "$HIST_DATA" ]]; then
                RESPONSE="HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n{\"error\": \"No data found for the requested time\"}"
            else
                RESPONSE="HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n$HIST_DATA"
            fi
        else
            # Serve real-time data
            LATEST_METRIC=$(tail -n 1 $PIPE)
            RESPONSE="HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n$LATEST_METRIC"
        fi

        # Send response back through the same connection
        echo -e "$RESPONSE"
    )
done
