#!/bin/sh
# A mounted volume is owned by root: give /data to the unprivileged user, then drop privileges.
set -e
mkdir -p "${MURAJA_DATA:-/data}"
if [ "$(id -u)" = "0" ]; then
  chown -R node:node "${MURAJA_DATA:-/data}"
  exec setpriv --reuid=node --regid=node --init-groups node server/index.ts
fi
exec node server/index.ts
