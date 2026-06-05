from __future__ import annotations

from typing import Any

from backend.app.core.database import (
    SessionLocal,
    create_database_tables,
)
from backend.app.seed.seed_boms import seed_boms
from backend.app.seed.seed_components import seed_components
from backend.app.seed.seed_gateways import seed_gateways


def _print_stats(
    label: str,
    stats: dict[str, int],
) -> None:
    print(
        f"{label}: "
        f"created={stats['created']}, "
        f"updated={stats['updated']}, "
        f"total={stats['total']}"
    )


def seed_all() -> dict[str, Any]:
    """Tạo bảng và nạp toàn bộ seed data của Day 2."""

    create_database_tables()

    with SessionLocal() as session:
        try:
            component_stats = seed_components(session)
            bom_stats = seed_boms(session)
            gateway_stats = seed_gateways(session)

            session.commit()
        except Exception:
            session.rollback()
            raise

    print("ZeroTag-Reel seed summary")
    print("-" * 40)

    _print_stats(
        "Components",
        component_stats,
    )

    _print_stats(
        "BOMs",
        bom_stats["boms"],
    )

    _print_stats(
        "BOM items",
        bom_stats["bom_items"],
    )

    _print_stats(
        "Gateways",
        gateway_stats,
    )

    print("-" * 40)
    print("Seed completed")

    return {
        "components": component_stats,
        "boms": bom_stats["boms"],
        "bom_items": bom_stats["bom_items"],
        "gateways": gateway_stats,
    }


if __name__ == "__main__":
    seed_all()