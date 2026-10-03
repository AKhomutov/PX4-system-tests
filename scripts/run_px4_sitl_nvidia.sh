#!/usr/bin/env bash
set -euo pipefail

instance="${1:-0}"

if ! [[ "$instance" =~ ^[0-9]+$ ]]; then
  echo "PX4 instance must be a non-negative integer" >&2
  exit 1
fi

container_name="px4-gazebo-$instance"
gz_partition="px4-test-$instance"
ros_domain_id=$((83 + instance))
IMAGE="${PX4_IMAGE:-px4io/px4-sitl-gazebo@sha256:aa4bbf35f0bd6bdb3269cc96e317c8e78b87f1fc769c734c0818094074e1cc0a}"

umask 077

: "${DISPLAY:?Open a terminal in your local graphical session}"

auth=$(mktemp)
trap 'rm -f "$auth"' EXIT

xauth nlist "$DISPLAY" |
  sed 's/^..../ffff/' |
  xauth -f "$auth" nmerge -

if [ ! -s "$auth" ]; then
  echo "No Xauthority cookie for $DISPLAY" >&2
  exit 1
fi

docker run --rm -it \
  --name "$container_name" \
  --network host \
  --gpus all \
  --mount type=bind,src=/tmp/.X11-unix,dst=/tmp/.X11-unix,readonly \
  --mount "type=bind,src=$auth,dst=/tmp/px4.xauth,readonly" \
  -e "DISPLAY=$DISPLAY" \
  -e XAUTHORITY=/tmp/px4.xauth \
  -e QT_QPA_PLATFORM=xcb \
  -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics,display \
  -e "GZ_PARTITION=$gz_partition" \
  -e "ROS_DOMAIN_ID=$ros_domain_id" \
  -e PX4_SIM_MODEL=gz_x500 \
  "$IMAGE" \
  -i "$instance"
