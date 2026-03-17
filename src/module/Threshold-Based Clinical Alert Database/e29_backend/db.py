from functools import lru_cache

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from e29_backend.config import MONGO_DB, MONGO_URI


@lru_cache
def get_client() -> MongoClient:
    return MongoClient(MONGO_URI)


@lru_cache
def get_database() -> Database:
    return get_client()[MONGO_DB]


def patient_groups_collection() -> Collection:
    return get_database()["Patient-group"]


def thresholds_collection() -> Collection:
    return get_database()["Threshold"]


def escalation_paths_collection() -> Collection:
    return get_database()["Escalation-path"]


def compliance_collection() -> Collection:
    return get_database()["Compliance"]


def ensure_indexes() -> None:
    patient_groups_collection().create_index("group_id", unique=True)
    thresholds_collection().create_index("threshold_id", unique=True)
    escalation_paths_collection().create_index("escalation_id", unique=True)
    compliance_collection().create_index("compliance_id", unique=True)
    thresholds_collection().create_index("group_id")
    escalation_paths_collection().create_index("threshold_id")
    compliance_collection().create_index("threshold_id")
    compliance_collection().create_index("check_timestamp")