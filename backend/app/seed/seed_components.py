from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.core.enums import (
    ComponentStatus,
    LabelType,
    TamperStatus,
)
from backend.app.models.component import Component
from backend.app.repositories.component_repo import (
    create_component,
    get_by_zerotag_id,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_COMPONENTS_CSV = (
    PROJECT_ROOT / "data" / "seed_csv" / "components.csv"
)

REQUIRED_COLUMNS = {
    "zerotag_id",
    "tag_uid",
    "part_number",
    "component_name",
    "manufacturer",
    "supplier",
    "lot_number",
    "date_code",
    "quantity_initial",
    "quantity_current",
    "status",
    "location",
    "label_type",
    "tamper_status",
}


def _required(
    row: dict[str, str],
    field: str,
    row_number: int,
) -> str:
    value = (row.get(field) or "").strip()

    if not value:
        raise ValueError(
            f"components.csv row {row_number}: "
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
            f"Component seed file was not found: {csv_path}"
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
                "components.csv is missing columns: "
                f"{sorted(missing_columns)}"
            )

        return [dict(row) for row in reader]


def seed_components(
    session: Session,
    *,
    csv_path: Path = DEFAULT_COMPONENTS_CSV,
) -> dict[str, int]:
    """Nạp hoặc cập nhật Component từ CSV."""

    created = 0
    updated = 0
    rows = _read_rows(csv_path)

    for row_number, row in enumerate(rows, start=2):
        zerotag_id = _required(
            row,
            "zerotag_id",
            row_number,
        )

        values = {
            "zerotag_id": zerotag_id,
            "tag_uid": _optional(row.get("tag_uid")),
            "part_number": _required(
                row,
                "part_number",
                row_number,
            ),
            "component_name": _required(
                row,
                "component_name",
                row_number,
            ),
            "manufacturer": _optional(
                row.get("manufacturer")
            ),
            "supplier": _optional(row.get("supplier")),
            "lot_number": _required(
                row,
                "lot_number",
                row_number,
            ),
            "date_code": _required(
                row,
                "date_code",
                row_number,
            ),
            "quantity_initial": int(
                _required(
                    row,
                    "quantity_initial",
                    row_number,
                )
            ),
            "quantity_current": int(
                _required(
                    row,
                    "quantity_current",
                    row_number,
                )
            ),
            "status": ComponentStatus(
                _required(
                    row,
                    "status",
                    row_number,
                )
            ),
            "location": _optional(row.get("location")),
            "label_type": LabelType(
                _required(
                    row,
                    "label_type",
                    row_number,
                )
            ),
            "tamper_status": TamperStatus(
                _required(
                    row,
                    "tamper_status",
                    row_number,
                )
            ),
        }

        component = get_by_zerotag_id(
            session,
            zerotag_id,
        )

        if component is None:
            create_component(
                session,
                Component(**values),
            )
            created += 1
            continue

        for field_name, field_value in values.items():
            setattr(
                component,
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