#!/bin/sh
# wait-for-postgres.sh

set -e

cmd="$@"

until psql -Atx $DATABASE_URL -c '\q'; do
  >&2 echo "postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "postgres is up - executing command"
exec $cmd
