#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset

OPERATOR_FILE="/etc/nats/DjangoOperator.conf"

until [ -f "$OPERATOR_FILE" ]; do
  >&2 echo 'Waiting for NATs to become available...'
  sleep 1
done
>&2 echo 'NATs is available'

# this if will check if the first argument is a flag
# but only works if all arguments require a hyphenated flag
# -v; -SL; -f arg; etc will work, but not arg1 arg2
if [ "$#" -eq 0 ] || [ "${1#-}" != "$1" ]; then
    set -- nats-server "$@"
fi

# else default to run whatever the user wanted like "bash" or "sh"
exec "$@" 