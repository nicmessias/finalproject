"""
Tests for BeHealthy Tracker Application
----------------------------------------
Author: Emiliano Acero and Nicole Messias
GitHub Username: eaceroyee1308 and nicmessias
Date: June 16, 2026
"""

import pytest
import json
import os
from project import log_entry, get_daily_summary, check_goals, load_data


# Use a separate test file so we never touch the real wellness_data.json
TEST_FILE = "test_wellness_data.json"


def setup_test_file():
    """Create a fresh test data file before each test."""
    data = {
        "goals": {
            "water": 8.0,
            "exercise": 30.0,
            "vitamins": True,
            "sleep": 8.0
        },
        "logs": {}
    }
    with open(TEST_FILE, "w") as f:
        json.dump(data, f)


def teardown_test_file():
    """Remove the test file after each test."""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)


# ── log_entry tests ────────────────────────────────────────────────────────────

def test_log_entry_returns_true():
    """log_entry should return True on success."""
    setup_test_file()
    result = log_entry("water", 6.0, date="2026-06-15", filename=TEST_FILE)
    assert result is True
    teardown_test_file()


def test_log_entry_saves_value():
    """log_entry should persist the correct value to the JSON file."""
    setup_test_file()
    log_entry("sleep", 7.5, date="2026-06-15", filename=TEST_FILE)
    data = load_data(TEST_FILE)
    assert data["logs"]["2026-06-15"]["sleep"]["value"] == 7.5
    teardown_test_file()


def test_log_entry_saves_notes():
    """log_entry should persist notes correctly."""
    setup_test_file()
    log_entry("exercise", 45.0, date="2026-06-15", notes="morning run", filename=TEST_FILE)
    data = load_data(TEST_FILE)
    assert data["logs"]["2026-06-15"]["exercise"]["notes"] == "morning run"
    teardown_test_file()


def test_log_entry_vitamins_bool():
    """log_entry should correctly store boolean value for vitamins."""
    setup_test_file()
    log_entry("vitamins", True, date="2026-06-15", filename=TEST_FILE)
    data = load_data(TEST_FILE)
    assert data["logs"]["2026-06-15"]["vitamins"]["value"] is True
    teardown_test_file()


# ── get_daily_summary tests ────────────────────────────────────────────────────

def test_get_daily_summary_no_data():
    """get_daily_summary should return status key when no data is logged."""
    setup_test_file()
    result = get_daily_summary(date="2026-06-01", filename=TEST_FILE)
    assert "status" in result
    teardown_test_file()


def test_get_daily_summary_with_data():
    """get_daily_summary should return categories when data exists."""
    setup_test_file()
    log_entry("water", 9.0, date="2026-06-15", filename=TEST_FILE)
    log_entry("exercise", 30.0, date="2026-06-15", filename=TEST_FILE)
    log_entry("vitamins", True, date="2026-06-15", filename=TEST_FILE)
    log_entry("sleep", 8.0, date="2026-06-15", filename=TEST_FILE)
    result = get_daily_summary(date="2026-06-15", filename=TEST_FILE)
    assert "categories" in result
    assert "water" in result["categories"]
    teardown_test_file()


def test_get_daily_summary_goal_met():
    """get_daily_summary should mark a category completed when goal is met."""
    setup_test_file()
    log_entry("water", 10.0, date="2026-06-15", filename=TEST_FILE)
    result = get_daily_summary(date="2026-06-15", filename=TEST_FILE)
    assert result["categories"]["water"]["completed"] is True
    teardown_test_file()


def test_get_daily_summary_goal_not_met():
    """get_daily_summary should mark a category not completed when goal is not met."""
    setup_test_file()
    log_entry("water", 3.0, date="2026-06-15", filename=TEST_FILE)
    result = get_daily_summary(date="2026-06-15", filename=TEST_FILE)
    assert result["categories"]["water"]["completed"] is False
    teardown_test_file()


# ── check_goals tests ──────────────────────────────────────────────────────────

def test_check_goals_no_data():
    """check_goals should return 0% completion when no data is logged."""
    setup_test_file()
    result = check_goals(date="2026-06-01", filename=TEST_FILE)
    assert result["completion_rate"] == 0.0
    assert result["completed_count"] == 0
    teardown_test_file()


def test_check_goals_all_met():
    """check_goals should return 100% when all goals are met."""
    setup_test_file()
    log_entry("water", 8.0, date="2026-06-15", filename=TEST_FILE)
    log_entry("exercise", 30.0, date="2026-06-15", filename=TEST_FILE)
    log_entry("vitamins", True, date="2026-06-15", filename=TEST_FILE)
    log_entry("sleep", 8.0, date="2026-06-15", filename=TEST_FILE)
    result = check_goals(date="2026-06-15", filename=TEST_FILE)
    assert result["completion_rate"] == 100.0
    assert result["completed_count"] == 4
    teardown_test_file()


def test_check_goals_partial():
    """check_goals should return correct partial completion rate."""
    setup_test_file()
    log_entry("water", 8.0, date="2026-06-15", filename=TEST_FILE)   # met
    log_entry("exercise", 10.0, date="2026-06-15", filename=TEST_FILE)  # not met
    log_entry("vitamins", True, date="2026-06-15", filename=TEST_FILE)  # met
    log_entry("sleep", 5.0, date="2026-06-15", filename=TEST_FILE)   # not met
    result = check_goals(date="2026-06-15", filename=TEST_FILE)
    assert result["completed_count"] == 2
    assert result["completion_rate"] == 50.0
    teardown_test_file()


def test_check_goals_total_always_four():
    """check_goals should always report 4 total goals."""
    setup_test_file()
    result = check_goals(date="2026-06-01", filename=TEST_FILE)
    assert result["total_goals"] == 4
    teardown_test_file()