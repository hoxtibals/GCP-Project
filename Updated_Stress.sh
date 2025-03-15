#!/bin/bash

# Log file location
LOGFILE="/opt/system-monitoring/logs/stress-test.log"

# Function to log activities
log_message() {
    echo "$(date) - $1" | tee -a $LOGFILE
}

# Generate random duration between 20-60 seconds
random_duration() {
    echo $((RANDOM % 41 + 20))
}

# Limit memory allocation to stay under 958MB (using 300-500MB for safety)
random_memory() {
    echo "$(( (RANDOM % 201 + 300) ))M"
}

# Generate random CPU load percentage (10-90%)
random_cpu_load() {
    echo $((RANDOM % 81 + 10))
}

# Generate random disk space (50-200MB)
random_disk_space() {
    echo "$(( (RANDOM % 151 + 50) ))M"
}

# Generate random I/O operations (100-500)
random_io_ops() {
    echo $((RANDOM % 401 + 100))
}

log_message "Starting system stress test with controlled parameters..."

# CPU stress with one worker and random load
CPU_DURATION=$(random_duration)
CPU_LOAD=$(random_cpu_load)
log_message "Applying CPU stress with 1 worker at ${CPU_LOAD}% load for $CPU_DURATION seconds..."
stress-ng --cpu 1 --cpu-load "$CPU_LOAD" --timeout "${CPU_DURATION}s"
log_message "CPU stress completed."

# Memory stress with controlled allocation
MEMORY_SIZE=$(random_memory)
MEMORY_DURATION=$(random_duration)
MEMORY_METHOD=$((RANDOM % 3))
MEMORY_METHOD_NAMES=("malloc" "mmap" "stack")
log_message "Applying Memory stress with $MEMORY_SIZE using ${MEMORY_METHOD_NAMES[$MEMORY_METHOD]} method for $MEMORY_DURATION seconds..."
stress-ng --vm 1 --vm-bytes "$MEMORY_SIZE" --vm-method "${MEMORY_METHOD_NAMES[$MEMORY_METHOD]}" --timeout "${MEMORY_DURATION}s"
log_message "Memory stress completed."

# Filesystem stress with smaller file size
HDD_DURATION=$(random_duration)
HDD_SIZE=$(random_disk_space)
log_message "Applying Filesystem stress with 1 worker creating ${HDD_SIZE} files for $HDD_DURATION seconds..."
stress-ng --hdd 1 --hdd-bytes "$HDD_SIZE" --timeout "${HDD_DURATION}s"
log_message "Filesystem stress completed."

# I/O stress with limited operations
IO_DURATION=$(random_duration)
IO_OPS=$(random_io_ops)
log_message "Applying I/O stress with 1 worker performing $IO_OPS ops for $IO_DURATION seconds..."
stress-ng --io 1 --io-ops "$IO_OPS" --timeout "${IO_DURATION}s"
log_message "I/O stress completed."

# Load Average stress (process spawning)
LOAD_DURATION=$(random_duration)
log_message "Applying Load Average stress with multiple processes for $LOAD_DURATION seconds..."
stress-ng --spawn 5 --spawn-ops 10 --timeout "${LOAD_DURATION}s"
log_message "Load Average stress completed."

# Power stress with controlled worker count
POWER_DURATION=$(random_duration)
POWER_METHODS=("bsqrt" "compute" "matrixprod" "cdouble")
SELECTED_POWER_METHOD=${POWER_METHODS[$RANDOM % ${#POWER_METHODS[@]}]}
log_message "Applying Power stress with 1 worker using $SELECTED_POWER_METHOD method for $POWER_DURATION seconds..."
stress-ng --cpu 1 --cpu-method "$SELECTED_POWER_METHOD" --timeout "${POWER_DURATION}s"
log_message "Power stress completed."

log_message "System stress test finished."
