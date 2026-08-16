#!/usr/bin/env python3
"""
Load Testing Suite for NaMo ACC Bot
Uses locust for distributed load testing
"""

import statistics
import time

from locust import HttpUser, between, events, task
from locust.contrib.fasthttp import FastHttpUser


class TelegramBotUser(FastHttpUser):
    """Simulates Telegram user interacting with ACC bot"""

    wait_time = between(2, 5)

    @task(4)
    def chat(self):
        """Send chat message"""
        payload = {
            "session_id": f"test_user_{self.client.base_url.split('/')[-1]}",
            "text": "Hi Vipha, how are you doing?",
        }

        with self.client.post("/session/chat", json=payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code: {response.status_code}")

    @task(1)
    def get_session_state(self):
        """Get current session state"""
        session_id = f"test_user_{self.client.base_url.split('/')[-1]}"

        with self.client.get(f"/session/{session_id}", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code: {response.status_code}")

    @task(2)
    def health_check(self):
        """Check health endpoint"""
        self.client.get("/health")


class AdminUser(HttpUser):
    """Simulates admin operations"""

    wait_time = between(5, 10)

    @task(1)
    def reset_session(self):
        """Reset session"""
        payload = {"session_id": "admin_test"}
        self.client.post("/session/reset", json=payload)

    @task(1)
    def telegram_webhook(self):
        """Simulate Telegram webhook"""
        payload = {
            "update_id": int(time.time()),
            "message": {
                "message_id": 1,
                "from": {"id": 12345, "is_bot": False, "first_name": "Test"},
                "chat": {"id": 12345, "type": "private"},
                "date": int(time.time()),
                "text": "Test message",
            },
        }
        self.client.post("/webhook/telegram", json=payload)


# Event handlers for reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n🚀 Load Test Starting...")
    print(f"Target: {environment.host}")
    print(f"Locust: {environment.locustfile}\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n\n📊 Load Test Summary:")
    print("=" * 60)

    # Calculate statistics
    total_requests = environment.stats.total.num_requests
    total_failures = environment.stats.total.num_failures
    success_rate = (
        ((total_requests - total_failures) / total_requests * 100) if total_requests > 0 else 0
    )

    response_times = []
    for request in environment.stats.entries.values():
        if hasattr(request, "response_times"):
            response_times.extend(request.response_times.values())

    if response_times:
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)

        print(f"Total Requests: {total_requests}")
        print(f"Total Failures: {total_failures}")
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Avg Response Time: {avg_response_time:.2f}ms")
        print(f"Min Response Time: {min_response_time:.2f}ms")
        print(f"Max Response Time: {max_response_time:.2f}ms")

    print("=" * 60 + "\n")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, **kwargs):
    """Log slow requests"""
    if response_time > 5000:  # 5 seconds
        print(f"⚠️  SLOW REQUEST: {name} ({response_time}ms)")
