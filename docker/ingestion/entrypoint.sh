#!/bin/bash

# Usage function to display help message
usage() {
    echo "Usage: $0 --start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD> --page-limit <int>"
    exit 1
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --start-date) start_date="$2"; shift ;;
        --end-date) end_date="$2"; shift ;;
        --page-limit) page_limit="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; usage ;;
    esac
    shift
done

# Check for required arguments
if [[ -z "$start_date" || -z "$end_date" || -z "$page_limit" ]]; then
    echo "Error: Missing required arguments."
    usage
fi

# List of site names
site_names=("handelsblatt" "tagesschau" "heise" "tagesspiegel" "spiegel")

# Create logs directory with today's date
today=$(date +%Y-%m-%d)
log_dir="logs/$today"
mkdir -p $log_dir

# Iterate through site names and launch separate processes
for site_name in "${site_names[@]}"; do
    log_file="$log_dir/$site_name.txt"
    nohup python -m pulsespotter.ingestion.scripts.content_ingestion \
        --start-date "$start_date" \
        --end-date "$end_date" \
        --page-limit "$page_limit" \
        --site-name "$site_name" > "$log_file" 2>&1 &
    echo "Started process for site_name: $site_name, logs at: $log_file"
done

wait
