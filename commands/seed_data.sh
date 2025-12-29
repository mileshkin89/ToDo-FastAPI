#!/usr/bin/env sh
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Starting database seeding..."

python -m database.populate

echo "Database seeding finished successfully."
