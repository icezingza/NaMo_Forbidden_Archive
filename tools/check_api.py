import argparse
import json
import os
import sys

import requests


def _normalize_base_url(raw_url: str) -> str:
    return raw_url.rstrip("/")


def _print_json_response(response: requests.Response) -> None:
    try:
        payload = response.json()
    except ValueError:
        print(response.text)
        return
    print(json.dumps(payload, indent=2, ensure_ascii=True))


def main() -> int:
    parser = argparse.ArgumentParser(description="Quick check for NaMo REST API.")
    parser.add_argument(
        "--base-url",
        default=os.getenv("NAMO_BASE_URL", "http://localhost:8000"),
        help="Base URL for the API (default: http://localhost:8000).",
    )
    parser.add_argument("--text", default="hello", help="Message to send to /chat.")
    parser.add_argument("--session-id", default="cli-check", help="Session ID to use.")
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds.")
    args = parser.parse_args()

    base_url = _normalize_base_url(args.base_url)
    root_url = f"{base_url}/"
    chat_url = f"{base_url}/chat"

    try:
        print(f"GET {root_url}")
        root_response = requests.get(root_url, timeout=args.timeout)
        print(f"Status: {root_response.status_code}")
        _print_json_response(root_response)
    except requests.RequestException as exc:
        print(f"Request failed: {exc}")
        return 1

    payload = {"text": args.text, "session_id": args.session_id}
    try:
        print(f"\nPOST {chat_url}")
        print(f"Payload: {payload}")
        chat_response = requests.post(chat_url, json=payload, timeout=args.timeout)
        print(f"Status: {chat_response.status_code}")
        _print_json_response(chat_response)
    except requests.RequestException as exc:
        print(f"Request failed: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
