#!/bin/bash

METRICS_SERVICE="metrics-api.service"
STRESS_SERVICE="stress-test.service"
LOG_FILE="/var/log/cron_job.log"

check_service() {
    local serviceName="$1"
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    if ! systemctl is-active --quiet "$serviceName"; then
        echo "[$TIMESTAMP] Service $serviceName is down. Attempting restart..." >> "$LOG_FILE"
        systemctl restart "$serviceName"

        if systemctl is-active --quiet "$serviceName"; then
            echo "[$TIMESTAMP] Service $serviceName successfully restarted" >> "$LOG_FILE"
        else
            echo "[$TIMESTAMP] Failed to restart service $serviceName" >> "$LOG_FILE"
        fi
    fi
}

# Check each service individually
check_service "$METRICS_SERVICE"
check_service "$STRESS_SERVICE"