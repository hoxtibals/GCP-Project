#!/bin/bash

PIPE="/tmp/metrics_pipe"
LOG_FILE="/opt/system-monitoring/logs/metrics.log"
PORT=5000

mkdir -p $(dirname "$LOG_FILE")

# Create the named pipe
if [[ ! -p $PIPE ]]; then
    mkfifo $PIPE
    chown root:monitoring $PIPE
    chmod 660 $PIPE # Group can read/write

fi

# what we will use to collect metrics (local use only)
collect_metrics() {
    while true; do
        TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
        CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
        MEM=$(free -m | awk 'NR==2{printf "%s/%s MB (%.2f%%)", $3, $2, $3*100/$2}')
        IO=$(iostat | awk 'NR==4 {print $1}')
        FS=$(df -h / | awk 'NR==2{print $5}')
        LOAD_AVG=$(cat /proc/loadavg | awk '{printf "%.2f", $1}')

        METRIC="{\"time\": \"$TIMESTAMP\", \"cpu\": \"$CPU%\", \"memory\": \"$MEM\", \"io\": \"$IO\", \"filesystem\": \"$FS\", \"load\": \"$LOAD_AVG\"}"

        echo "$METRIC"
        echo "$METRIC" > $PIPE #we run writing to the pipe in the background to prevent stoppage
        echo "$METRIC" >> $LOG_FILE  # Store for history

        sleep 5  #HERE WE CAN CHANGE OUR INTERVAL FOR TESTS
    done
}

# Start collecting metrics in background and start logging
collect_metrics &

# API Server
while true; do
#read request using
    RESPONSE_FILE=$(mktemp)
    nc -l -s 0.0.0.0 -p $PORT -q 1 > /tmp/request.tmp 
        REQUEST=$(cat /tmp/request.tmp)
        rm -f /tmp/request.tmp

        # Check if request is for history
        if echo "$REQUEST" | grep -q "/history?time="; then
            REQ_TIME=$(echo "$REQUEST" | grep -oP "(?<=/history\?time=)[0-9]{2}:[0-9]{2}")
            # Format today's date for comparison
            TODAY=$(date "+%Y-%m-%d")
            # Get current time minus 1 minute
            CURRENT_TIME=$(date "+%H:%M")
            #we would use awk to better handle strings and be able to compare time
            #@note THIS IS ONLY GRABING DATA FROM TODAY
                        # ...existing code...
            
            # Modify the awk command to collect all matching entries
            HIST_DATA=$(awk -v start="$TODAY $REQ_TIME" -v end="$TODAY $CURRENT_TIME" '
                BEGIN { printf "[" }
                /"time"/ {
                    match($0, /time[[:space:]]*:[[:space:]]*"([^"]+)"/, timestamp)
                    ts = timestamp[1]
                    if (ts >= start && ts <= end) {
                        if (first) printf "," 
                        print $0
                        first=1
                    }
                }
                END { printf "]" }
            ' "$LOG_FILE")
            
            # Increase timeout for history response
            if [[ -n "$HIST_DATA" ]]; then
                {
                    echo -en "HTTP/1.1 200 OK\r\n"
                    echo -en "Connection: close\r\n"
                    echo -en "Content-Type: application/json\r\n"
                    echo -en "Content-Length: ${#HIST_DATA}\r\n"
                    echo -en "\r\n"
                    echo -en "$HIST_DATA"
                } > "$RESPONSE_FILE"
            fi
            
            # Use longer timeout for history response
            cat "$RESPONSE_FILE" | nc -l -s 0.0.0.0 -p $PORT -q 10

            if [[ -z "$HIST_DATA" ]]; then
                {
                    echo -en "HTTP/1.1 404 Not Found\r\n"
                    echo -en "Connection: close\r\n"
                    echo -en "Content-Type: application/json\r\n"
                    echo -en "Content-Length: 47\r\n"
                    echo -en "\r\n"
                    echo -en '{"error": "No data found for the requested time"}'
                } > "$RESPONSE_FILE"
            else
                {
                    echo -en "HTTP/1.1 200 OK\r\n"
                    echo -en "Connection: close\r\n"
                    echo -en "Content-Type: application/json\r\n"
                    echo -en "Content-Length: ${#HIST_DATA}\r\n"
                    echo -en "\r\n"
                    echo -en "$HIST_DATA"
                } > "$RESPONSE_FILE"
            fi
         else
            LATEST_METRIC=$(dd if="$PIPE" bs=4096 count=1 2>/dev/null)
            
            if [[ -n "$LATEST_METRIC" ]]; then
                {
                    echo -en "HTTP/1.1 200 OK\r\n"
                    echo -en "Connection: close\r\n"
                    echo -en "Content-Type: application/json\r\n"
                    echo -en "Content-Length: ${#LATEST_METRIC}\r\n"
                    echo -en "\r\n"
                    echo -en "$LATEST_METRIC"
                } > "$RESPONSE_FILE"
            fi
        fi
    cat "$RESPONSE_FILE" | nc -l -s 127.0.0.1 -p $PORT -q 1
    # Cleanup
    rm -f "$RESPONSE_FILE"
done