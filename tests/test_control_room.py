"""Unit tests for NRE Control Room Subsystem."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from core.control_room import (
    AgentRegistry,
    ArchitectureAnalyzer,
    BackupManager,
    ControlRoomManager,
    CronPlanner,
    SecurityAuditor,
    SystemTaskRouter,
)


def test_architecture_analyzer():
    analyzer = ArchitectureAnalyzer()
    res = analyzer.analyze("Micro-service Architecture", context="Scaling issue")

    assert res["status"] == "completed"
    assert "steps" in res
    assert "1_STATE" in res["steps"]
    assert "3_PRIORITY" in res["steps"]
    assert "7_METRIC" in res["steps"]


def test_agent_registry():

    registry = AgentRegistry()
    summary = registry.get_summary()

    assert summary["total_engines"] >= 5
    assert summary["online_engines"] >= 5

    # Test update status
    assert registry.update_status("omega", "offline", active_sessions=2) is True
    engine = registry.get_engine("omega")
    assert engine["status"] == "offline"
    assert engine["active_sessions"] == 2

    # Test unknown engine
    assert registry.update_status("nonexistent", "online") is False


def test_system_task_router():
    router = SystemTaskRouter()

    # Test explicit override
    res1 = router.route("hello world", requested_engine="dark")
    assert res1["target_engine"] == "dark"
    assert res1["is_explicit_override"] is True

    # Test keyword matching
    res2 = router.route("tell me a dark smut story")
    assert res2["target_engine"] == "dark"
    assert res2["is_explicit_override"] is False

    res3 = router.route("sensual erotic fusion with rinlada")
    assert res3["target_engine"] == "rinlada"

    # Test fallback
    res4 = router.route("how is the weather today?")
    assert res4["target_engine"] == "omega"


def test_backup_manager(tmp_path: Path):
    # Create fake files in tmp_path
    (tmp_path / "memory_history.json").write_text("{}", encoding="utf-8")
    (tmp_path / "vector_db").mkdir()
    (tmp_path / "vector_db" / "test.index").write_text("index data", encoding="utf-8")

    mgr = BackupManager(base_dir=tmp_path, backup_dir=tmp_path / "backups", max_backups=2)
    summary = mgr.trigger_backup()

    assert summary["status"] == "success"
    assert summary["file_count"] >= 2
    assert (tmp_path / "backups" / summary["archive_name"]).exists()

    backups_list = mgr.list_backups()
    assert len(backups_list) == 1


def test_security_auditor(tmp_path: Path):
    (tmp_path / ".gitignore").write_text(".env\n__pycache__/\n", encoding="utf-8")
    (tmp_path / "system.yaml").write_text("config: ok\n", encoding="utf-8")

    auditor = SecurityAuditor(base_dir=tmp_path)
    report = auditor.run_audit()

    assert "overall_status" in report
    assert report["total_checks"] >= 3
    findings_ids = [f["id"] for f in report["findings"]]
    assert "SEC-001" in findings_ids


@pytest.mark.asyncio
async def test_cron_planner():
    planner = CronPlanner()
    run_counter = {"count": 0}

    async def sample_task():
        run_counter["count"] += 1

    planner.register_task("sample", interval_seconds=1, coro_func=sample_task)
    tasks_list = planner.list_tasks()
    assert len(tasks_list) == 1
    assert tasks_list[0]["name"] == "sample"

    await planner.start()
    await asyncio.sleep(1.5)
    await planner.stop()

    assert run_counter["count"] >= 1


def test_control_room_manager(tmp_path: Path):
    manager = ControlRoomManager(base_dir=tmp_path)
    full_status = manager.get_full_status()

    assert full_status["control_room"] == "active"
    assert "registry" in full_status
    assert "backups" in full_status
    assert "security" in full_status
    assert "tasks" in full_status
