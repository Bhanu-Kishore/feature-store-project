"""Apply Feast definitions and materialize the static snapshot into SQLite."""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
os.chdir(REPO_ROOT)
sys.path.insert(0, str(REPO_ROOT))

from feast import FeatureStore  # noqa: E402

from feature_definitions import customer, customer_features  # noqa: E402

# The Telco snapshot carries one synthetic timestamp (2026-01-01) for every
# customer, so the materialization window only needs to cover that instant.
MATERIALIZE_START = datetime(2025, 1, 1, tzinfo=timezone.utc)
MATERIALIZE_END = datetime(2030, 1, 1, tzinfo=timezone.utc)


def main() -> None:
    store = FeatureStore(repo_path=str(REPO_ROOT))
    store.apply([customer, customer_features])
    store.materialize(start_date=MATERIALIZE_START, end_date=MATERIALIZE_END)
    print("Feast registry applied and online store materialized.")


if __name__ == "__main__":
    main()
