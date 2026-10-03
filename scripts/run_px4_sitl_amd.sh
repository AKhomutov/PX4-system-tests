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

# Mesa/AMD (and Intel) GPU acceleration via DRM render devices, as documented by PX4:
# https://docs.px4.io/main/en/simulation/gazebo_container_gui
# Requires /dev/dri on the host (card*/renderD*).
docker run --rm -it \
  --name "$container_name" \
  --network host \
  --device=/dev/dri \
  --mount type=bind,src=/tmp/.X11-unix,dst=/tmp/.X11-unix,readonly \
  --mount "type=bind,src=$auth,dst=/tmp/px4.xauth,readonly" \
  -e "DISPLAY=$DISPLAY" \
  -e XAUTHORITY=/tmp/px4.xauth \
  -e QT_QPA_PLATFORM=xcb \
  -e "GZ_PARTITION=$gz_partition" \
  -e "ROS_DOMAIN_ID=$ros_domain_id" \
  -e PX4_SIM_MODEL=gz_x500 \
  px4io/px4-sitl-gazebo:latest \
  -i "$instance"
