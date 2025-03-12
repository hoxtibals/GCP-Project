#!/bin/bash

# Log file location
LOGFILE="/var/log/stress-test.log"

# Function to log activities
log_message() {
    echo "$(date) - $1" | tee -a $LOGFILE
}

log_message "Starting system stress test..."

# Apply CPU stress (4 workers for 30 seconds)
log_message "Applying CPU stress..."
stress-ng --cpu 4 --timeout 30s
log_message "CPU stress completed."

# Apply Memory stress (1GB allocated for 30 seconds)
log_message "Applying Memory stress..."
stress-ng --vm 2 --vm-bytes 1G --timeout 30s
log_message "Memory stress completed."

# Apply Filesystem stress (temporary file writes for 30 seconds)
log_message "Applying Filesystem stress..."
stress-ng --hdd 2 --timeout 30s
log_message "Filesystem stress completed."

# Apply I/O stress (high disk activity for 30 seconds)
log_message "Applying I/O stress..."
stress-ng --io 4 --timeout 30s
log_message "I/O stress completed."

# Apply Power stress (CPU power stress for 30 seconds)
log_message "Applying Power stress..."
stress-ng --cpu 4 --cpu-method power --timeout 30s
log_message "Power stress completed."

log_message "System stress test finished."
