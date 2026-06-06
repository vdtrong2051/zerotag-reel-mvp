from __future__ import annotations

from datetime import datetime
from typing import Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from backend.app.core.enums import (
    BuzzerAction,
    ComponentStatus,
    EventType,
    LedAction,
    ScanMode,
    ScanResult,
)


class ScanRequest(BaseModel):
    """Payload scan thống nhất từ Dashboard hoặc Gateway."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "request_id": "REQ-BOM-VALID-0001",
                    "gateway_id": "ZG-001",
                    "mode": "BOM_CHECK",
                    "location": "SMT Issue Station 01",
                    "zerotag_id": "ZT-R1001",
                    "tag_uid": "UID-R1001",
                    "qr_id": None,
                    "rfid_id": None,
                    "bom_code": "PCB-DEMO-01",
                    "bom_ref": "R12",
                    "read_at": "2026-06-06T09:30:00+07:00",
                }
            ]
        },
    )

    request_id: str = Field(
        min_length=1,
        max_length=128,
    )

    gateway_id: str = Field(
        min_length=1,
        max_length=64,
    )

    mode: ScanMode

    location: str = Field(
        min_length=1,
        max_length=255,
    )

    zerotag_id: str | None = Field(
        default=None,
        max_length=64,
    )

    tag_uid: str | None = Field(
        default=None,
        max_length=128,
    )

    qr_id: str | None = Field(
        default=None,
        max_length=64,
    )

    rfid_id: str | None = Field(
        default=None,
        max_length=64,
    )

    bom_code: str | None = Field(
        default=None,
        max_length=64,
    )

    bom_ref: str | None = Field(
        default=None,
        max_length=64,
    )

    read_at: datetime

    @field_validator(
        "zerotag_id",
        "tag_uid",
        "qr_id",
        "rfid_id",
        "bom_code",
        "bom_ref",
        mode="before",
    )
    @classmethod
    def normalize_optional_strings(
        cls,
        value: Any,
    ) -> Any:
        """Chuyển chuỗi rỗng thành None."""

        if isinstance(value, str):
            cleaned = value.strip()

            return cleaned or None

        return value

    @field_validator("read_at")
    @classmethod
    def validate_read_at_timezone(
        cls,
        value: datetime,
    ) -> datetime:
        """Thời gian Gateway đọc tag phải có timezone."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                "read_at must include timezone information."
            )

        return value

    @model_validator(mode="after")
    def validate_fields_by_mode(self) -> Self:
        """Kiểm tra field bắt buộc theo từng scan mode."""

        component_modes = {
            ScanMode.INBOUND,
            ScanMode.BOM_CHECK,
            ScanMode.RETURN,
        }

        if (
            self.mode in component_modes
            and self.zerotag_id is None
            and self.tag_uid is None
        ):
            raise ValueError(
                "zerotag_id or tag_uid is required "
                f"for mode {self.mode.value}."
            )

        if self.mode == ScanMode.BOM_CHECK:
            missing_fields: list[str] = []

            if self.bom_code is None:
                missing_fields.append("bom_code")

            if self.bom_ref is None:
                missing_fields.append("bom_ref")

            if missing_fields:
                raise ValueError(
                    "BOM_CHECK requires: "
                    + ", ".join(missing_fields)
                    + "."
                )

        if self.mode == ScanMode.VERIFY:
            missing_fields = []

            if self.qr_id is None:
                missing_fields.append("qr_id")

            if self.rfid_id is None:
                missing_fields.append("rfid_id")

            if missing_fields:
                raise ValueError(
                    "VERIFY requires: "
                    + ", ".join(missing_fields)
                    + "."
                )

        return self


class GatewayAction(BaseModel):
    """Lệnh phản hồi vật lý cho Gateway."""

    model_config = ConfigDict(
        extra="forbid",
    )

    led: LedAction
    buzzer: BuzzerAction


class ComponentSnapshot(BaseModel):
    """Snapshot Component tại thời điểm xử lý scan."""

    model_config = ConfigDict(
        extra="forbid",
    )

    zerotag_id: str
    part_number: str
    lot_number: str
    date_code: str

    quantity_current: int = Field(ge=0)

    status_before: ComponentStatus
    status_after: ComponentStatus

    location: str | None = None


class BomCheckSnapshot(BaseModel):
    """Thông tin BOMItem được dùng để đối chiếu."""

    model_config = ConfigDict(
        extra="forbid",
    )

    bom_code: str
    bom_ref: str

    required_part_number: str
    required_lot: str | None = None

    allowed_date_code_from: str | None = None
    allowed_date_code_to: str | None = None

    required_quantity: int = Field(ge=1)
    quantity_sufficient: bool


class ScanResponse(BaseModel):
    """Response thống nhất cho Dashboard và Gateway Simulator."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "request_id": "REQ-BOM-VALID-0001",
                    "transaction_id": "TX-000001",
                    "mode": "BOM_CHECK",
                    "status": "VALID",
                    "message": (
                        "Component matches the selected BOM item."
                    ),
                    "event_type": "BOM_MATCH_OK",
                    "violations": [],
                    "component": {
                        "zerotag_id": "ZT-R1001",
                        "part_number": "RES-10K-0603",
                        "lot_number": "L2026A01",
                        "date_code": "2520",
                        "quantity_current": 5000,
                        "status_before": "IN_STOCK",
                        "status_after": "IN_STOCK",
                        "location": "Warehouse A1",
                    },
                    "bom_check": {
                        "bom_code": "PCB-DEMO-01",
                        "bom_ref": "R12",
                        "required_part_number": "RES-10K-0603",
                        "required_lot": "L2026A01",
                        "allowed_date_code_from": "2520",
                        "allowed_date_code_to": "2540",
                        "required_quantity": 100,
                        "quantity_sufficient": True,
                    },
                    "gateway_action": {
                        "led": "GREEN",
                        "buzzer": "SHORT_BEEP",
                    },
                    "replayed": False,
                    "processed_at": (
                        "2026-06-06T09:30:01+07:00"
                    ),
                }
            ]
        },
    )

    request_id: str
    transaction_id: str

    mode: ScanMode
    status: ScanResult

    message: str
    event_type: EventType

    violations: list[ScanResult] = Field(
        default_factory=list,
    )

    component: ComponentSnapshot | None = None
    bom_check: BomCheckSnapshot | None = None

    gateway_action: GatewayAction

    replayed: bool = False
    processed_at: datetime

    @field_validator("processed_at")
    @classmethod
    def validate_processed_at_timezone(
        cls,
        value: datetime,
    ) -> datetime:
        """Thời điểm backend xử lý xong phải có timezone."""

        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(
                "processed_at must include timezone information."
            )

        return value