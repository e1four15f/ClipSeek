#!/bin/bash

# Specify the input/output directory containing your mp4 files
input_dir="data/MSRVTT/videos/all"
output_dir="data/MSRVTT/videos/5sec"
num_jobs=12  # processors
clip_duration=5  # seconds

# Create output directory if it doesn't exist
mkdir -p "$output_dir"

# Function to split a single video into clips
split_video() {
    local file="$1"
    local output_dir="$2"
    local clip_duration="$3"
    local filename=$(basename "$file" .mp4)
    ffmpeg -i "$file" -acodec copy -f segment -segment_time $clip_duration -vcodec copy -reset_timestamps 1 -map 0 "$output_dir/$filename-%04d.mp4"
}
export -f split_video

# Run split_video function in parallel for each mp4 file
find "$input_dir" -type f -name '*.mp4' | parallel split_video {} "$output_dir" "$clip_duration"
