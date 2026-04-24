import json
import os
import random
import uuid
from datetime import datetime

LOG_STORE_DIR = os.getenv("LOG_STORE_DIR", "logs")

SERVICES = ["api-gateway", "auth-service", "order-service", "inventory-service", "db"]
LEVELS = ["INFO", "WARN", "ERROR"]


def make_log_entry(request_id: str, service: str, level: str, message: str, details: dict | None = None) -> dict:
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "request_id": request_id,
        "service": service,
        "level": level,
        "message": message,
        "details": details or {},
    }


def generate_sample_logs() -> list:
    logs = []
    request_ids = [str(uuid.uuid4()) for _ in range(3)]

    for request_id in request_ids:
        logs.append(make_log_entry(request_id, "api-gateway", "INFO", "Received request", {"path": "/checkout"}))
        logs.append(make_log_entry(request_id, "auth-service", "INFO", "Validated auth token", {"user_id": random.randint(1000, 9999)}))

        if random.random() < 0.5:
            logs.append(make_log_entry(request_id, "order-service", "ERROR", "Order processing failed", {"error_code": "ORDER_TIMEOUT", "timeout_ms": 12000}))
            logs.append(make_log_entry(request_id, "inventory-service", "WARN", "Inventory lookup slow", {"latency_ms": 850}))
            logs.append(make_log_entry(request_id, "db", "ERROR", "DB query failed", {"query": "UPDATE orders SET status='failed' WHERE id=?", "error": "deadlock detected"}))
        else:
            logs.append(make_log_entry(request_id, "order-service", "INFO", "Order completed successfully", {"order_id": random.randint(10000, 99999)}))
            logs.append(make_log_entry(request_id, "inventory-service", "INFO", "Inventory reserved", {"item_id": random.randint(100, 999)}))
            logs.append(make_log_entry(request_id, "db", "INFO", "DB update succeeded", {"rows_affected": 1}))

    return logs


def write_logs(logs: list) -> None:
    os.makedirs(LOG_STORE_DIR, exist_ok=True)
    path = os.path.join(LOG_STORE_DIR, "sample_logs.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(logs, handle, indent=2, ensure_ascii=False)
    print(f"Generated {len(logs)} log entries in: {path}")


if __name__ == "__main__":
    sample_logs = generate_sample_logs()
    write_logs(sample_logs)
