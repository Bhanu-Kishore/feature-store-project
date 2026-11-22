#!/usr/bin/env sh
set -eu

cd /app
mkdir -p /app/data

# A mounted persistent volume starts empty, so seed it from the snapshot that
# was built into the image. Existing files are never overwritten.
for file in telco_features.parquet registry.db online_store.db; do
    if [ ! -f "/app/data/$file" ] && [ -f "/app/seed/$file" ]; then
        cp "/app/seed/$file" "/app/data/$file"
    fi
done

if [ "${FORCE_FEAST_BOOTSTRAP:-0}" = "1" ]; then
    python scripts/build_feature_store.py
fi

exec "$@"
