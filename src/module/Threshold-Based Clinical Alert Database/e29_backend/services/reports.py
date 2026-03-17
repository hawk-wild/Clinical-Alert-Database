from e29_backend.db import compliance_collection


def compliance_summary() -> dict:
    total = compliance_collection().count_documents({})
    violations = compliance_collection().count_documents({"violation_status": "Violation"})
    within_limit = compliance_collection().count_documents({"violation_status": "Within Limit"})
    violation_rate = round((violations / total) * 100, 2) if total else 0

    pipeline = [
        {
            "$group": {
                "_id": "$threshold_id",
                "total_checks": {"$sum": 1},
                "violations": {
                    "$sum": {
                        "$cond": [{"$eq": ["$violation_status", "Violation"]}, 1, 0]
                    }
                },
            }
        },
        {
            "$project": {
                "_id": 0,
                "threshold_id": "$_id",
                "total_checks": 1,
                "violations": 1,
                "violation_rate": {
                    "$cond": [
                        {"$eq": ["$total_checks", 0]},
                        0,
                        {"$multiply": [{"$divide": ["$violations", "$total_checks"]}, 100]},
                    ]
                },
            }
        },
    ]

    by_threshold = list(compliance_collection().aggregate(pipeline))
    for item in by_threshold:
        item["violation_rate"] = round(item["violation_rate"], 2)

    return {
        "total_checks": total,
        "violations": violations,
        "within_limit": within_limit,
        "violation_rate": violation_rate,
        "by_threshold": by_threshold,
    }