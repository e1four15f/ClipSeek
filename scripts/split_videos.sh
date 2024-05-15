#!/bin/bash

# Specify the input/output directory containing your videos
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
    local filename=$(basename "$file")
    local extension="${filename##*.}"

    if [[ $extension == "mp4" ]]; then
        ffmpeg -i "$file" -acodec copy -f segment -segment_time $clip_duration -vcodec copy -reset_timestamps 1 -map 0 "$output_dir/${filename%.*}-%04d.mp4"
    elif [[ $extension == "avi" ]]; then
        ffmpeg -i "$file" -acodec copy -bsf:v h264_mp4toannexb -f segment -segment_time $clip_duration -vcodec copy -reset_timestamps 1 -map 0 "$output_dir/${filename%.*}-%04d.avi"
    else
        echo "Unsupported format for file: $file"
    fi
}
export -f split_video

# Run split_video function in parallel for each video file
find "$input_dir" -type f \( -name '*.mp4' -o -name '*.avi' \) | parallel split_video {} "$output_dir" "$clip_duration"