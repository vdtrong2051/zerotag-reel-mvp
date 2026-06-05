from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.core.enums import (
    GatewayStatus,
    GatewayType,
)
from backend.app.models.gateway import Gateway
from backend.app.repositories.gateway_repo import (
    create_gateway,
    get_by_gateway_id,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GATEWAYS_CSV = (
    PROJECT_ROOT / "data" / "seed_csv" / "gateways.csv"
)

REQUIRED_COLUMNS = {
    "gateway_id",
    "gateway_name",
    "gateway_type",
    "location",
    "status",
}


def _required(
    row: dict[str, str],
    field: str,
    row_number: int,
) -> str:
    value = (row.get(field) or "").strip()

    if not value:
        raise ValueError(
            f"gateways.csv row {row_number}: "
            f"field '{field}' is required."
        )

    return value


def _optional(value: str | None) -> str | None:
    cleaned = (value or "").strip()

    return cleaned or None


def _read_rows(
    csv_path: Path,
) -> list[dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Gateway seed file was not found: {csv_path}"
        )

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = set(reader.fieldnames or [])

        missing_columns = REQUIRED_COLUMNS - fieldnames

        if missing_columns:
            raise ValueError(
                "gateways.csv is missing columns: "
                f"{sorted(missing_columns)}"
            )

        return [dict(row) for row in reader]


def seed_gateways(
    session: Session,
    *,
    csv_path: Path = DEFAULT_GATEWAYS_CSV,
) -> dict[str, int]:
    """Nạp hoặc cập nhật Gateway từ CSV."""

    created = 0
    updated = 0
    rows = _read_rows(csv_path)

    for row_number, row in enumerate(rows, start=2):
        gateway_id = _required(
            row,
            "gateway_id",
            row_number,
        )

        values = {
            "gateway_id": gateway_id,
            "gateway_name": _required(
                row,
                "gateway_name",
                row_number,
            ),
            "gateway_type": GatewayType(
                _required(
                    row,
                    "gateway_type",
                    row_number,
                )
            ),
            "location": _optional(row.get("location")),
            "status": GatewayStatus(
                _required(
                    row,
                    "status",
                    row_number,
                )
            ),
        }

        gateway = get_by_gateway_id(
            session,
            gateway_id,
        )

        if gateway is None:
            create_gateway(
                session,
                Gateway(**values),
            )
            created += 1
            continue

        for field_name, field_value in values.items():
            setattr(
                gateway,
                field_name,
                field_value,
            )

        updated += 1

    session.flush()

    return {
        "created": created,
        "updated": updated,
        "total": len(rows),
    }