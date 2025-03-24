#!/bin/bash

PIPE="/tmp/metrics_pipe"
LOG_FILE="/opt/system-monitoring/logs/metrics.log"
PORT=5000

mkdir -p $(dirname "$LOG_FILE")

# Create the named pipe


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
    nc -l -s 0.0.0.0 -p $PORT -q 1 | {
        read -r REQUEST
        rm -f "$RESPONSE_FILE"
        LATEST_METRIC=$(dd if="$PIPE" bs=4096 count=1 2>/dev/null)

            if [[ -z "$LATEST_METRIC" ]] && [[ -f "$LOG_FILE" ]]; then
                LATEST_METRIC=$(tail -n 1 "$LOG_FILE")
                echo "Pipe empty, using last log entry: $LATEST_METRIC"
            fi
            
            if [[ -n "$LATEST_METRIC" ]]; then
                {
                    echo -en "HTTP/1.1 200 OK\r\n"
                    echo -en "Connection: close\r\n"
                    echo -en "Content-Type: application/json\r\n"
                    echo -en "Content-Length: ${#LATEST_METRIC}\r\n"
                    echo -en "\r\n"
                    echo -en "$LATEST_METRIC"
                } > "$RESPONSE_FILE"
            else
                # No data available in pipe or log
                ERROR_MSG='{"error": "No metrics available"}'
                {
                    echo -en "HTTP/1.1 503 Service Unavailable\r\n"
                    echo -en "Connection: close\r\n"
                    echo -en "Content-Type: application/json\r\n"
                    echo -en "Content-Length: ${#ERROR_MSG}\r\n"
                    echo -en "\r\n"
                    echo -en "$ERROR_MSG"
                } > "$RESPONSE_FILE"
            fi
    cat "$RESPONSE_FILE"
    # Cleanupv
    }
       
done