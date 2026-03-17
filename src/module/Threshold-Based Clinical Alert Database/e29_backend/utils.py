from datetime import datetime, timezone


def serialize_doc(doc: dict | None) -> dict | None:
    if not doc:
        return None
    payload = dict(doc)
    payload["_id"] = str(payload["_id"])
    return payload


def serialize_many(docs: list[dict]) -> list[dict]:
    return [serialize_doc(doc) for doc in docs if doc]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def next_id(prefix: str, count: int) -> str:
    return f"{prefix}{count + 1:03d}"