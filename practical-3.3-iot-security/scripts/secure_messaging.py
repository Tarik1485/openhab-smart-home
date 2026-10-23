import hashlib
import hmac
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "security.log"

# Демонстраційний ключ для лабораторної роботи.
# Для реальної системи потрібне захищене керування ключами.
DEVICE_KEY = b"iot-lab-demo-key-change-in-production"

# Зберігаємо ідентифікатори вже прийнятих повідомлень.
seen_nonces = set()


def log_event(message):
    """Записує подію безпеки в журнал."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")


def calculate_hmac(payload):
    """Обчислює HMAC-SHA256 для повідомлення."""
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")

    return hmac.new(
        DEVICE_KEY, encoded, hashlib.sha256
    ).hexdigest()


def create_message(device_id, temperature):
    """Створює підписане повідомлення від датчика."""
    payload = {
        "device_id": device_id,
        "temperature": temperature,
        "timestamp": int(time.time()),
        "nonce": str(time.time_ns()),
    }

    return {
        "payload": payload,
        "hmac": calculate_hmac(payload),
    }


def verify_message(message):
    """Перевіряє автентичність, час і повторне надсилання."""
    payload = message.get("payload")
    signature = message.get("hmac")

    if not isinstance(payload, dict) or not isinstance(signature, str):
        log_event("REJECTED: invalid message format")
        return False

    expected_signature = calculate_hmac(payload)

    if not hmac.compare_digest(signature, expected_signature):
        log_event("REJECTED: invalid HMAC")
        return False

    timestamp = payload.get("timestamp")
    nonce = payload.get("nonce")

    if not isinstance(timestamp, int) or not isinstance(nonce, str):
        log_event("REJECTED: missing timestamp or nonce")
        return False

    if abs(int(time.time()) - timestamp) > 60:
        log_event("REJECTED: message outside allowed time window")
        return False

    if nonce in seen_nonces:
        log_event("REJECTED: replay attack detected")
        return False

    seen_nonces.add(nonce)
    log_event(f"ACCEPTED: message from {payload.get('device_id')}")
    return True


def main():
    print("=== IoT Secure Messaging Demo ===")

    message = create_message("sensor-01", 22.5)

    print("\n1. Перевірка звичайного повідомлення:")
    print("Прийнято:", verify_message(message))

    print("\n2. Повторне надсилання того самого повідомлення:")
    print("Прийнято:", verify_message(message))

    print("\n3. Повідомлення зі зміненою температурою:")
    tampered_message = {
        "payload": dict(message["payload"]),
        "hmac": message["hmac"],
    }
    tampered_message["payload"]["temperature"] = 99.9
    print("Прийнято:", verify_message(tampered_message))

    print(f"\nЖурнал безпеки: {LOG_FILE}")


if __name__ == "__main__":
    main()