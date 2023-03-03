import pytest
from unittest.mock import patch, mock_open

import json
import sys
import argparse
from pathlib import Path

import story_threads

WHOLE_THREAD = {
	"0": {"antagonist in disguise":
		{"event": "open", "description": "antagonist in disguise"}},
	"1": {"antagonist in disguise":
		{"event": "develop", "description": "fake-ally knows"}},
	"2": {"antagonist in disguise":
		{"event": "close", "description": "antagonists disguise fails"}}}

OPEN_THREAD = {
	"0": {"protagonist feels lonely":
		{"event": "open", "description": "protagonist feels lonely"}},
	"2": {"protagonist feels lonely":
		{"event": "develop", "description": "protagonist gains a friend"}}}

WHOLE_THREAD_FIRST = {
	"0": {"protagonist feels lonely":
		{"event": "open", "description": "protagonist feels lonely"}},
	"1": {"antagonist in disguise":
		{"event": "open", "description": "antagonist in disguise"}},
	"2": {"antagonist in disguise":
		{"event": "develop", "description": "fake-ally knows"}},
	"3": {"protagonist feels lonely":
		{"event": "develop", "description": "protagonist gains a friend"}},
	"4": {"antagonist in disguise":
		{"event": "close", "description": "antagonists disguise fails"}}}

OPEN_THREAD_FIRST = {
	"0": {"antagonist in disguise":
		{"event": "open", "description": "antagonist in disguise"}},
	"1": {"protagonist feels lonely":
		{"event": "open", "description": "protagonist feels lonely"}},
	"2": {"antagonist in disguise":
		{"event": "develop", "description": "fake-ally knows"}},
	"3": {"protagonist feels lonely":
		{"event": "develop", "description": "protagonist gains a friend"}},
	"4": {"antagonist in disguise":
		{"event": "close", "description": "antagonists disguise fails"}}}

ARGS = argparse.Namespace(
	story = "runtests",
	path = "",
	show_connections = False,
	names = [WHOLE_THREAD[i][next(iter(WHOLE_THREAD[i].keys()))]["description"] for i in WHOLE_THREAD.keys()],
	indices = [int(i) for i in WHOLE_THREAD.keys()],
	close = True if "close" in [WHOLE_THREAD[i][next(iter(WHOLE_THREAD[i].keys()))]["event"] for i in WHOLE_THREAD.keys()] else False
)

def test_add_whole_thread(tmp_path):
	expected = WHOLE_THREAD
	ARGS.path = tmp_path

	#with patch.object(sys, "argv",
	#["story-threads.py", "runtests", "add",
	#expected["0"][next(iter(expected["0"].keys()))]["description"], expected["1"][next(iter(expected["1"].keys()))]["description"], expected["2"][next(iter(expected["2"].keys()))]["description"],
	#"-i", "0", "1", "2", "-c"]):
	story_threads.add_thread(ARGS)
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_same_thread_twice(tmp_path):
	with pytest.raises(ValueError) as e:
		expected = WHOLE_THREAD
		ARGS.path = tmp_path

		story_threads.add_thread(ARGS)
		story_threads.add_thread(ARGS)

def test_add_open_thread(monkeypatch, tmp_path):
	expected = OPEN_THREAD
	monkeypatch.setitem(expected, "1", expected["2"])
	monkeypatch.delitem(expected, "2")
	ARGS.path = tmp_path
	monkeypatch.setattr(ARGS, "names", [OPEN_THREAD[i][next(iter(OPEN_THREAD[i].keys()))]["description"] for i in OPEN_THREAD.keys()])
	monkeypatch.setattr(ARGS, "indices", [int(i) for i in OPEN_THREAD.keys()])
	monkeypatch.setattr(ARGS, "close", True if "close" in [OPEN_THREAD[i][next(iter(OPEN_THREAD[i].keys()))]["event"] for i in OPEN_THREAD.keys()] else False)

	story_threads.add_thread(ARGS)
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_whole_thread_first(monkeypatch, tmp_path):
	expected = WHOLE_THREAD_FIRST
	ARGS.path = tmp_path

	story_threads.add_thread(ARGS)
	monkeypatch.setattr(ARGS, "names", [OPEN_THREAD[i][next(iter(OPEN_THREAD[i].keys()))]["description"] for i in OPEN_THREAD.keys()])
	monkeypatch.setattr(ARGS, "indices", [int(i) for i in OPEN_THREAD.keys()])
	monkeypatch.setattr(ARGS, "close", True if "close" in [OPEN_THREAD[i][next(iter(OPEN_THREAD[i].keys()))]["event"] for i in OPEN_THREAD.keys()] else False)
	story_threads.add_thread(ARGS)
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_open_thread_first(monkeypatch, tmp_path):
	expected = OPEN_THREAD_FIRST
	ARGS.path = tmp_path

	with monkeypatch.context() as m:
		m.setattr(ARGS, "names", [OPEN_THREAD[i][next(iter(OPEN_THREAD[i].keys()))]["description"] for i in OPEN_THREAD.keys()])
		m.setattr(ARGS, "indices", [int(i) for i in OPEN_THREAD.keys()])
		m.setattr(ARGS, "close", True if "close" in [OPEN_THREAD[i][next(iter(OPEN_THREAD[i].keys()))]["event"] for i in OPEN_THREAD.keys()] else False)
		story_threads.add_thread(ARGS)
	story_threads.add_thread(ARGS)
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected
