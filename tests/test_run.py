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
	names = [],
	indices = [],
	close = None
)


def get_descriptions(thread):
	"""
	List all descriptions from the given thread

	Return:
		list: A list of all descriptions from the given thread
	"""
	descriptions = []
	for k in thread.keys():
		try:
			descriptions.append(thread[k][next(iter(thread[k].keys()))]["description"])
		except KeyError:
			pass
	return descriptions

def thread_closes(thread):
	"""
	Check if the given thread is closed

	Return:
		Boolean: True if the thread closes, else False
	"""
	return True if "close" in [thread[i][next(iter(thread[i].keys()))]["event"] for i in thread.keys()] else False


def test_add_whole_thread(monkeypatch, tmp_path):
	expected = WHOLE_THREAD

	ARGS.path = tmp_path
	monkeypatch.setattr(ARGS, "names", get_descriptions(WHOLE_THREAD))
	monkeypatch.setattr(ARGS, "indices", [int(i) for i in WHOLE_THREAD.keys()])
	monkeypatch.setattr(ARGS, "close", thread_closes(WHOLE_THREAD))

	story_threads.add_thread(ARGS)
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_same_thread_twice(monkeypatch, tmp_path):
	with pytest.raises(ValueError) as e:
		expected = WHOLE_THREAD

		ARGS.path = tmp_path
		monkeypatch.setattr(ARGS, "names", get_descriptions(WHOLE_THREAD))
		monkeypatch.setattr(ARGS, "indices", [int(i) for i in WHOLE_THREAD.keys()])
		monkeypatch.setattr(ARGS, "close", thread_closes(WHOLE_THREAD))

		story_threads.add_thread(ARGS)
		story_threads.add_thread(ARGS)

def test_add_open_thread(monkeypatch, tmp_path):
	expected = OPEN_THREAD
	# since there is no second element, the second element will be
	# stored at position 1 in the thread list
	monkeypatch.setitem(expected, "1", expected["2"])
	monkeypatch.delitem(expected, "2")

	ARGS.path = tmp_path
	monkeypatch.setattr(ARGS, "names", get_descriptions(OPEN_THREAD))
	monkeypatch.setattr(ARGS, "indices", [int(i) for i in OPEN_THREAD.keys()])
	monkeypatch.setattr(ARGS, "close", thread_closes(OPEN_THREAD))

	story_threads.add_thread(ARGS)
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_whole_thread_first(monkeypatch, tmp_path):
	expected = WHOLE_THREAD_FIRST

	ARGS.path = tmp_path
	with monkeypatch.context() as m:
		m.setattr(ARGS, "names", get_descriptions(WHOLE_THREAD))
		m.setattr(ARGS, "indices", [int(i) for i in WHOLE_THREAD.keys()])
		m.setattr(ARGS, "close", thread_closes(WHOLE_THREAD))
		story_threads.add_thread(ARGS)
	monkeypatch.setattr(ARGS, "names", get_descriptions(OPEN_THREAD))
	monkeypatch.setattr(ARGS, "indices", [int(i) for i in OPEN_THREAD.keys()])
	monkeypatch.setattr(ARGS, "close", thread_closes(OPEN_THREAD))
	story_threads.add_thread(ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_open_thread_first(monkeypatch, tmp_path):
	expected = OPEN_THREAD_FIRST

	ARGS.path = tmp_path
	with monkeypatch.context() as m:
		m.setattr(ARGS, "names", get_descriptions(OPEN_THREAD))
		m.setattr(ARGS, "indices", [int(i) for i in OPEN_THREAD.keys()])
		m.setattr(ARGS, "close", thread_closes(OPEN_THREAD))
		story_threads.add_thread(ARGS)
	monkeypatch.setattr(ARGS, "names", get_descriptions(WHOLE_THREAD))
	monkeypatch.setattr(ARGS, "indices", [int(i) for i in WHOLE_THREAD.keys()])
	monkeypatch.setattr(ARGS, "close", thread_closes(WHOLE_THREAD))
	story_threads.add_thread(ARGS)
	
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_closed_without_description(monkeypatch, tmp_path):
	expected = WHOLE_THREAD
	# remove the description from the closing event
	new_close = expected["2"]
	new_close[next(iter(expected["2"].keys()))]["description"] = ""
	monkeypatch.setitem(expected, "2", new_close)

	ARGS.path = tmp_path
	monkeypatch.setattr(ARGS, "names", get_descriptions(WHOLE_THREAD)[:-1])
	monkeypatch.setattr(ARGS, "indices", [int(i) for i in WHOLE_THREAD.keys()])
	monkeypatch.setattr(ARGS, "close", thread_closes(WHOLE_THREAD))

	story_threads.add_thread(ARGS)
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected


# test closing without description
# test adding to existing thread
# test error cases:
#- pass empty lists
#- pass missing development description -> ValueError
#- pass missing development description with already open thread -> ValueError
#- pass correct thread in different order (e.g. first close, then develop, then open)
#- pass wrong event order (first close, then develop or open and first develop or open then close) -> ValueError
#- develop with same text

# test remove thread and change thread
# test showthread?
