from datetime import datetime, timezone
from typing import Any, overload


@overload
def serialize_doc(doc: None) -> None:
    ...


@overload
def serialize_doc(doc: dict[str, Any]) -> dict[str, Any]:
    ...


def serialize_doc(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    if not doc:
        return None
    payload = dict(doc)
    payload["_id"] = str(payload["_id"])
    return payload


def serialize_many(docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [serialize_doc(doc) for doc in docs]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def next_id(prefix: str, count: int) -> str:
    return f"{prefix}{count + 1:03d}"