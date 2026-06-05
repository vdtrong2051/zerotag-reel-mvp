from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy.orm import Session

from backend.app.core.enums import BomStatus
from backend.app.models.bom import Bom
from backend.app.models.bom_item import BomItem
from backend.app.repositories.bom_repo import (
    create_bom,
    create_bom_item,
    get_by_bom_code,
    get_item_by_ref,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SEED_CSV_DIR = PROJECT_ROOT / "data" / "seed_csv"

DEFAULT_BOMS_CSV = SEED_CSV_DIR / "boms.csv"
DEFAULT_BOM_ITEMS_CSV = SEED_CSV_DIR / "bom_items.csv"

BOM_REQUIRED_COLUMNS = {
    "bom_code",
    "product_name",
    "description",
    "status",
}

BOM_ITEM_REQUIRED_COLUMNS = {
    "bom_code",
    "bom_ref",
    "required_part_number",
    "allowed_lot",
    "allowed_date_code_from",
    "allowed_date_code_to",
    "required_quantity",
    "note",
}


def _required(
    row: dict[str, str],
    field: str,
    row_number: int,
    filename: str,
) -> str:
    value = (row.get(field) or "").strip()

    if not value:
        raise ValueError(
            f"{filename} row {row_number}: "
            f"field '{field}' is required."
        )

    return value


def _optional(value: str | None) -> str | None:
    cleaned = (value or "").strip()

    return cleaned or None


def _read_rows(
    csv_path: Path,
    required_columns: set[str],
) -> list[dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"BOM seed file was not found: {csv_path}"
        )

    with csv_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = set(reader.fieldnames or [])

        missing_columns = required_columns - fieldnames

        if missing_columns:
            raise ValueError(
                f"{csv_path.name} is missing columns: "
                f"{sorted(missing_columns)}"
            )

        return [dict(row) for row in reader]


def _seed_bom_headers(
    session: Session,
    csv_path: Path,
) -> dict[str, int]:
    created = 0
    updated = 0
    rows = _read_rows(
        csv_path,
        BOM_REQUIRED_COLUMNS,
    )

    for row_number, row in enumerate(rows, start=2):
        bom_code = _required(
            row,
            "bom_code",
            row_number,
            csv_path.name,
        )

        values = {
            "bom_code": bom_code,
            "product_name": _required(
                row,
                "product_name",
                row_number,
                csv_path.name,
            ),
            "description": _optional(
                row.get("description")
            ),
            "status": BomStatus(
                _required(
                    row,
                    "status",
                    row_number,
                    csv_path.name,
                )
            ),
        }

        bom = get_by_bom_code(
            session,
            bom_code,
            include_items=False,
        )

        if bom is None:
            create_bom(
                session,
                Bom(**values),
            )
            created += 1
            continue

        for field_name, field_value in values.items():
            setattr(
                bom,
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


def _seed_bom_items(
    session: Session,
    csv_path: Path,
) -> dict[str, int]:
    created = 0
    updated = 0
    rows = _read_rows(
        csv_path,
        BOM_ITEM_REQUIRED_COLUMNS,
    )

    for row_number, row in enumerate(rows, start=2):
        bom_code = _required(
            row,
            "bom_code",
            row_number,
            csv_path.name,
        )

        bom_ref = _required(
            row,
            "bom_ref",
            row_number,
            csv_path.name,
        )

        bom = get_by_bom_code(
            session,
            bom_code,
            include_items=False,
        )

        if bom is None:
            raise ValueError(
                f"{csv_path.name} row {row_number}: "
                f"BOM '{bom_code}' does not exist."
            )

        values = {
            "bom_id": bom.id,
            "bom_ref": bom_ref,
            "required_part_number": _required(
                row,
                "required_part_number",
                row_number,
                csv_path.name,
            ),
            "allowed_lot": _optional(
                row.get("allowed_lot")
            ),
            "allowed_date_code_from": _optional(
                row.get("allowed_date_code_from")
            ),
            "allowed_date_code_to": _optional(
                row.get("allowed_date_code_to")
            ),
            "required_quantity": int(
                _required(
                    row,
                    "required_quantity",
                    row_number,
                    csv_path.name,
                )
            ),
            "note": _optional(row.get("note")),
        }

        bom_item = get_item_by_ref(
            session,
            bom_code=bom_code,
            bom_ref=bom_ref,
        )

        if bom_item is None:
            create_bom_item(
                session,
                BomItem(**values),
            )
            created += 1
            continue

        for field_name, field_value in values.items():
            setattr(
                bom_item,
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


def seed_boms(
    session: Session,
    *,
    boms_csv_path: Path = DEFAULT_BOMS_CSV,
    bom_items_csv_path: Path = DEFAULT_BOM_ITEMS_CSV,
) -> dict[str, dict[str, int]]:
    """Nạp BOM trước, sau đó nạp BOMItem."""

    bom_stats = _seed_bom_headers(
        session,
        boms_csv_path,
    )

    bom_item_stats = _seed_bom_items(
        session,
        bom_items_csv_path,
    )

    return {
        "boms": bom_stats,
        "bom_items": bom_item_stats,
    }