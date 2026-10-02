#!/usr/bin/env bash
set -euo pipefail

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
  --name px4-gazebo \
  --network host \
  --gpus all \
  --mount type=bind,src=/tmp/.X11-unix,dst=/tmp/.X11-unix,readonly \
  --mount "type=bind,src=$auth,dst=/tmp/px4.xauth,readonly" \
  -e "DISPLAY=$DISPLAY" \
  -e XAUTHORITY=/tmp/px4.xauth \
  -e QT_QPA_PLATFORM=xcb \
  -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics,display \
  -e ROS_DOMAIN_ID=83 \
  -e PX4_SIM_MODEL=gz_x500 \
  px4io/px4-sitl-gazebo:latest
