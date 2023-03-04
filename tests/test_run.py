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

TWO_DEVS_THREAD = {
	"0": {"hero searches artifact":
		{"event": "open", "description": "hero searches artifact"}},
	"1": {"hero searches artifact":
		{"event": "develop", "description": "hero finds the first clue"}},
	"2": {"hero searches artifact":
		{"event": "develop", "description": "hero finds the final clue"}},
	"3": {"hero searches artifact":
		{"event": "close"}}}

ADD_ARGS = argparse.Namespace(
	story = "runtests",
	path = "",
	show_connections = False,
	names = [],
	indices = [],
	close = None
)

RM_ARGS = argparse.Namespace(
	story = "runtests",
	path = "",
	show_connections = False,
	name = "",
	development = "",
	ending = False
)

C_ARGS = argparse.Namespace(
	story = "runtests",
	path = "",
	show_connections = False,
	name = "",
	opening = [],
	development = [],
	ending = []
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


### test add ###

def test_add_whole_thread(monkeypatch, tmp_path):
	expected = WHOLE_THREAD

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", get_descriptions(WHOLE_THREAD))
	monkeypatch.setattr(ADD_ARGS, "indices", [int(i) for i in WHOLE_THREAD.keys()])
	monkeypatch.setattr(ADD_ARGS, "close", thread_closes(WHOLE_THREAD))

	story_threads.add_thread(ADD_ARGS)
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_same_thread_twice(monkeypatch, tmp_path):
	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", get_descriptions(WHOLE_THREAD))
	monkeypatch.setattr(ADD_ARGS, "indices", [int(i) for i in WHOLE_THREAD.keys()])
	monkeypatch.setattr(ADD_ARGS, "close", thread_closes(WHOLE_THREAD))

	with pytest.raises(ValueError) as e:
		story_threads.add_thread(ADD_ARGS)
		story_threads.add_thread(ADD_ARGS)

def test_add_open_thread(monkeypatch, tmp_path):
	expected = OPEN_THREAD
	# since there is no second element, the second element will be
	# stored at position 1 in the thread list
	monkeypatch.setitem(expected, "1", expected["2"])
	monkeypatch.delitem(expected, "2")

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", get_descriptions(OPEN_THREAD))
	monkeypatch.setattr(ADD_ARGS, "indices", [int(i) for i in OPEN_THREAD.keys()])
	monkeypatch.setattr(ADD_ARGS, "close", thread_closes(OPEN_THREAD))

	story_threads.add_thread(ADD_ARGS)
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_whole_thread_first(monkeypatch, tmp_path):
	expected = WHOLE_THREAD_FIRST

	ADD_ARGS.path = tmp_path
	with monkeypatch.context() as m:
		m.setattr(ADD_ARGS, "names", get_descriptions(WHOLE_THREAD))
		m.setattr(ADD_ARGS, "indices", [int(i) for i in WHOLE_THREAD.keys()])
		m.setattr(ADD_ARGS, "close", thread_closes(WHOLE_THREAD))
		story_threads.add_thread(ADD_ARGS)
	monkeypatch.setattr(ADD_ARGS, "names", get_descriptions(OPEN_THREAD))
	monkeypatch.setattr(ADD_ARGS, "indices", [int(i) for i in OPEN_THREAD.keys()])
	monkeypatch.setattr(ADD_ARGS, "close", thread_closes(OPEN_THREAD))
	story_threads.add_thread(ADD_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_open_thread_first(monkeypatch, tmp_path):
	expected = OPEN_THREAD_FIRST

	ADD_ARGS.path = tmp_path
	with monkeypatch.context() as m:
		m.setattr(ADD_ARGS, "names", get_descriptions(OPEN_THREAD))
		m.setattr(ADD_ARGS, "indices", [int(i) for i in OPEN_THREAD.keys()])
		m.setattr(ADD_ARGS, "close", thread_closes(OPEN_THREAD))
		story_threads.add_thread(ADD_ARGS)
	monkeypatch.setattr(ADD_ARGS, "names", get_descriptions(WHOLE_THREAD))
	monkeypatch.setattr(ADD_ARGS, "indices", [int(i) for i in WHOLE_THREAD.keys()])
	monkeypatch.setattr(ADD_ARGS, "close", thread_closes(WHOLE_THREAD))
	story_threads.add_thread(ADD_ARGS)
	
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_closed_without_description(monkeypatch, tmp_path):
	expected = WHOLE_THREAD
	# remove the description from the closing event
	new_close = expected["2"]
	new_close[next(iter(expected["2"].keys()))]["description"] = ""
	monkeypatch.setitem(expected, "2", new_close)

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", get_descriptions(WHOLE_THREAD)[:-1])
	monkeypatch.setattr(ADD_ARGS, "indices", [int(i) for i in WHOLE_THREAD.keys()])
	monkeypatch.setattr(ADD_ARGS, "close", thread_closes(WHOLE_THREAD))

	story_threads.add_thread(ADD_ARGS)
	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_development(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	thread_d = "ally knows"

	expected = WHOLE_THREAD
	monkeypatch.setitem(expected, "3", expected["2"])
	monkeypatch.setitem(expected, "2", {"antagonist in disguise":
		{"event": "develop", "description": thread_d}})

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", ["antagonist in disguise", thread_d])
	monkeypatch.setattr(ADD_ARGS, "indices", ["2"])
	monkeypatch.setattr(ADD_ARGS, "close", False)

	story_threads.add_thread(ADD_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_end(monkeypatch, tmp_path):
	expected = OPEN_THREAD
	monkeypatch.setitem(expected, "1", expected["2"])
	monkeypatch.delitem(expected, "2")

	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(expected, f, ensure_ascii=False)

	monkeypatch.setitem(expected, "2", {"protagonist feels lonely":
		{"event": "close", "description": ""}})

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", ["protagonist feels lonely"])
	monkeypatch.setattr(ADD_ARGS, "indices", ["2"])
	monkeypatch.setattr(ADD_ARGS, "close", True)

	story_threads.add_thread(ADD_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_empty_thread_indices(monkeypatch, tmp_path):
	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", ["whatever"])
	monkeypatch.setattr(ADD_ARGS, "indices", [])
	monkeypatch.setattr(ADD_ARGS, "close", False)

	with pytest.raises(ValueError) as e:
		story_threads.add_thread(ADD_ARGS)

def test_add_empty_thread_names(monkeypatch, tmp_path):
	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", [])
	monkeypatch.setattr(ADD_ARGS, "indices", ["1"])
	monkeypatch.setattr(ADD_ARGS, "close", False)

	with pytest.raises(ValueError) as e:
		story_threads.add_thread(ADD_ARGS)

def test_add_missing_description_no_end(monkeypatch, tmp_path):
	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", ["new thread opening"])
	monkeypatch.setattr(ADD_ARGS, "indices", ["1", "2"])
	monkeypatch.setattr(ADD_ARGS, "close", False)

	with pytest.raises(ValueError) as e:
		story_threads.add_thread(ADD_ARGS)

def test_add_missing_description_with_end(monkeypatch, tmp_path):
	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", ["new thread opening"])
	monkeypatch.setattr(ADD_ARGS, "indices", ["1", "2", "3"])
	monkeypatch.setattr(ADD_ARGS, "close", True)

	with pytest.raises(ValueError) as e:
		story_threads.add_thread(ADD_ARGS)

def test_add_development_with_same_description(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	thread_d = get_descriptions(WHOLE_THREAD)[1]

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", ["antagonist in disguise", thread_d])
	monkeypatch.setattr(ADD_ARGS, "indices", ["2"])
	monkeypatch.setattr(ADD_ARGS, "close", False)

	with pytest.raises(ValueError) as e:
		story_threads.add_thread(ADD_ARGS)

def test_add_ending_to_closed_thread(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", ["antagonist in disguise", "end"])
	monkeypatch.setattr(ADD_ARGS, "indices", ["7"])
	monkeypatch.setattr(ADD_ARGS, "close", True)

	with pytest.raises(ValueError) as e:
		story_threads.add_thread(ADD_ARGS)

def test_add_whole_thread_opening_last(monkeypatch, tmp_path):
	expected = WHOLE_THREAD

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", get_descriptions(WHOLE_THREAD)[1:] + [get_descriptions(WHOLE_THREAD)[0]])
	resorted_indices = [int(i) for i in WHOLE_THREAD.keys()]
	resorted_indices.append(resorted_indices.pop(0)) 
	monkeypatch.setattr(ADD_ARGS, "indices", resorted_indices)
	monkeypatch.setattr(ADD_ARGS, "close", thread_closes(WHOLE_THREAD))

	with pytest.raises(ValueError) as e:
		story_threads.add_thread(ADD_ARGS)

def test_add_whole_thread_end_first(monkeypatch, tmp_path):
	expected = WHOLE_THREAD

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", [get_descriptions(WHOLE_THREAD)[-1]] + get_descriptions(WHOLE_THREAD)[:-1])
	resorted_indices = [int(i) for i in WHOLE_THREAD.keys()]
	resorted_indices.insert(0, resorted_indices.pop())
	monkeypatch.setattr(ADD_ARGS, "indices", resorted_indices)
	monkeypatch.setattr(ADD_ARGS, "close", thread_closes(WHOLE_THREAD))

	with pytest.raises(ValueError) as e:
		story_threads.add_thread(ADD_ARGS)

def test_add_whole_thread_develop_first(monkeypatch, tmp_path):
	expected = WHOLE_THREAD

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", [get_descriptions(WHOLE_THREAD)[1]] + [get_descriptions(WHOLE_THREAD)[0]] + get_descriptions(WHOLE_THREAD)[2:])
	resorted_indices = [int(i) for i in WHOLE_THREAD.keys()]
	resorted_indices.insert(0, resorted_indices.pop(1))
	monkeypatch.setattr(ADD_ARGS, "indices", resorted_indices)
	monkeypatch.setattr(ADD_ARGS, "close", thread_closes(WHOLE_THREAD))

	with pytest.raises(ValueError) as e:
		story_threads.add_thread(ADD_ARGS)

def test_add_whole_thread_develop_last(monkeypatch, tmp_path):
	expected = WHOLE_THREAD

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", [get_descriptions(WHOLE_THREAD)[0]] + get_descriptions(WHOLE_THREAD)[2:] + [get_descriptions(WHOLE_THREAD)[1]])
	resorted_indices = [int(i) for i in WHOLE_THREAD.keys()]
	resorted_indices.append(resorted_indices.pop(1))
	monkeypatch.setattr(ADD_ARGS, "indices", resorted_indices)
	monkeypatch.setattr(ADD_ARGS, "close", thread_closes(WHOLE_THREAD))

	with pytest.raises(ValueError) as e:
		story_threads.add_thread(ADD_ARGS)

def test_add_multiple_developments(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	thread_d = ["ally knows", "antagonist changes disguise"]

	expected = WHOLE_THREAD
	monkeypatch.setitem(expected, "4", expected["2"])
	monkeypatch.setitem(expected, "2", {"antagonist in disguise":
		{"event": "develop", "description": thread_d[0]}})
	monkeypatch.setitem(expected, "3", {"antagonist in disguise":
		{"event": "develop", "description": thread_d[1]}})

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", ["antagonist in disguise"] + thread_d)
	monkeypatch.setattr(ADD_ARGS, "indices", ["2", "2"])
	monkeypatch.setattr(ADD_ARGS, "close", False)

	story_threads.add_thread(ADD_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_multiple_developments_wrong_order(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	thread_d = ["ally knows", "antagonist changes disguise"]

	expected = WHOLE_THREAD
	monkeypatch.setitem(expected, "4", expected["2"])
	monkeypatch.setitem(expected, "2", {"antagonist in disguise":
		{"event": "develop", "description": thread_d[0]}})
	monkeypatch.setitem(expected, "3", {"antagonist in disguise":
		{"event": "develop", "description": thread_d[1]}})

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", ["antagonist in disguise"] + list(reversed(thread_d)))
	monkeypatch.setattr(ADD_ARGS, "indices", ["2", "1"])
	monkeypatch.setattr(ADD_ARGS, "close", False)

	story_threads.add_thread(ADD_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_add_end_before_dev(monkeypatch, tmp_path):
	fixes_indices_thread = OPEN_THREAD
	monkeypatch.setitem(fixes_indices_thread, "1", fixes_indices_thread["2"])
	monkeypatch.delitem(fixes_indices_thread, "2")
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(fixes_indices_thread, f, ensure_ascii=False)

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", ["protagonist feels lonely"])
	monkeypatch.setattr(ADD_ARGS, "indices", ["1"])
	monkeypatch.setattr(ADD_ARGS, "close", True)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		story_threads.add_thread(ADD_ARGS)

def test_add_dev_after_end(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	ADD_ARGS.path = tmp_path
	monkeypatch.setattr(ADD_ARGS, "names", ["antagonist in disguise", "ally knows"])
	monkeypatch.setattr(ADD_ARGS, "indices", ["3"])
	monkeypatch.setattr(ADD_ARGS, "close", False)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		story_threads.add_thread(ADD_ARGS)


### test remove ###

def test_remove_entire_thread(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD_FIRST, f, ensure_ascii=False)

	expected = OPEN_THREAD
	monkeypatch.setitem(expected, "1", expected["2"])
	monkeypatch.delitem(expected, "2")

	RM_ARGS.path = tmp_path
	monkeypatch.setattr(RM_ARGS, "name", "antagonist in disguise")

	story_threads.remove_thread(RM_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_remove_everything(monkeypatch, tmp_path):
	expected = {}

	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	RM_ARGS.path = tmp_path
	monkeypatch.setattr(RM_ARGS, "name", "antagonist in disguise")

	story_threads.remove_thread(RM_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_remove_ending(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	expected = WHOLE_THREAD
	monkeypatch.delitem(expected, "2")

	RM_ARGS.path = tmp_path
	monkeypatch.setattr(RM_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(RM_ARGS, "ending", True)

	story_threads.remove_thread(RM_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_remove_dev_and_ending(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	expected = WHOLE_THREAD
	monkeypatch.delitem(expected, "1")
	monkeypatch.delitem(expected, "2")

	RM_ARGS.path = tmp_path
	monkeypatch.setattr(RM_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(RM_ARGS, "development", ["1"])
	monkeypatch.setattr(RM_ARGS, "ending", True)

	story_threads.remove_thread(RM_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_remove_only_specific_dev_by_index(monkeypatch, tmp_path):
	expected = TWO_DEVS_THREAD
	monkeypatch.setitem(expected, "3", {"hero searches artifact":
		{"event": "close", "description": ""}})

	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(TWO_DEVS_THREAD, f, ensure_ascii=False)

	monkeypatch.setitem(expected, "2", expected["3"])
	monkeypatch.delitem(expected, "3")

	RM_ARGS.path = tmp_path
	monkeypatch.setattr(RM_ARGS, "name", "hero searches artifact")
	monkeypatch.setattr(RM_ARGS, "development", ["2"])

	story_threads.remove_thread(RM_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_remove_only_specific_dev_by_description(monkeypatch, tmp_path):
	expected = TWO_DEVS_THREAD
	monkeypatch.setitem(expected, "3", {"hero searches artifact":
		{"event": "close", "description": ""}})

	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(TWO_DEVS_THREAD, f, ensure_ascii=False)

	monkeypatch.setitem(expected, "2", expected["3"])
	monkeypatch.delitem(expected, "3")

	RM_ARGS.path = tmp_path
	monkeypatch.setattr(RM_ARGS, "name", "hero searches artifact")
	monkeypatch.setattr(RM_ARGS, "development", ["hero finds the final clue"])

	story_threads.remove_thread(RM_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_remove_multiple_devs(monkeypatch, tmp_path):
	expected = TWO_DEVS_THREAD
	monkeypatch.setitem(expected, "3", {"hero searches artifact":
		{"event": "close", "description": ""}})

	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(TWO_DEVS_THREAD, f, ensure_ascii=False)

	monkeypatch.setitem(expected, "1", expected["3"])
	monkeypatch.delitem(expected, "2")
	monkeypatch.delitem(expected, "3")

	RM_ARGS.path = tmp_path
	monkeypatch.setattr(RM_ARGS, "name", "hero searches artifact")
	monkeypatch.setattr(RM_ARGS, "development", ["1", "hero finds the final clue"])

	story_threads.remove_thread(RM_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_remove_non_existing_ending(monkeypatch, tmp_path):
	RM_ARGS.path = tmp_path
	monkeypatch.setattr(RM_ARGS, "name", "protagonist feels lonely")
	monkeypatch.setattr(RM_ARGS, "ending", True)

	with pytest.raises(ValueError) as e:
		story_threads.remove_thread(RM_ARGS)

def test_remove_non_existing_thread(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	RM_ARGS.path = tmp_path
	monkeypatch.setattr(RM_ARGS, "name", "protagonist feels lonely")
	monkeypatch.setattr(RM_ARGS, "ending", True)

	with pytest.raises(ValueError) as e:
		story_threads.remove_thread(RM_ARGS)


### test change ###

def test_rename_opening(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	new_description = "antagonist is disguised"

	expected = WHOLE_THREAD
	monkeypatch.setitem(expected, "0", {"antagonist in disguise":
		{"event": "open", "description": new_description}})

	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "opening", [new_description])

	story_threads.change_thread(C_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_rename_dev_by_index(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	new_description = "fake-ally learns about disguise"

	expected = WHOLE_THREAD
	monkeypatch.setitem(expected, "1", {"antagonist in disguise":
		{"event": "develop", "description": new_description}})

	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "development", ["1", new_description])

	story_threads.change_thread(C_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_rename_dev_by_description(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	new_description = "fake-ally learns about disguise"

	expected = WHOLE_THREAD
	monkeypatch.setitem(expected, "1", {"antagonist in disguise":
		{"event": "develop", "description": new_description}})

	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "development", ["fake-ally knows", new_description])

	story_threads.change_thread(C_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_rename_ending(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD, f, ensure_ascii=False)

	new_description = "antagonists disguise is discovered by protagonist"

	expected = WHOLE_THREAD
	monkeypatch.setitem(expected, "2", {"antagonist in disguise":
		{"event": "close", "description": new_description}})

	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "ending", [new_description])

	story_threads.change_thread(C_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_change_pos_ending(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD_FIRST, f, ensure_ascii=False)

	expected = WHOLE_THREAD_FIRST
	temp = expected["3"]
	monkeypatch.setitem(expected, "3", expected["4"])
	monkeypatch.setitem(expected, "4", temp)

	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "ending", ["3"])

	story_threads.change_thread(C_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_change_pos_opening(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD_FIRST, f, ensure_ascii=False)

	expected = WHOLE_THREAD_FIRST
	temp = expected["0"]
	monkeypatch.setitem(expected, "0", expected["1"])
	monkeypatch.setitem(expected, "1", temp)

	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "opening", ["0"])

	story_threads.change_thread(C_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_change_pos_dev(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD_FIRST, f, ensure_ascii=False)

	expected = WHOLE_THREAD_FIRST
	temp = expected["2"]
	monkeypatch.setitem(expected, "2", expected["3"])
	monkeypatch.setitem(expected, "3", temp)

	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "development", ["2", "3"])

	story_threads.change_thread(C_ARGS)

	with open(Path(tmp_path, "runtests.json"), "r") as f:
		result = json.load(f)
		assert result == expected

def test_change_pos_ending_to_opening(monkeypatch, tmp_path):
	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "ending", ["0"])

	with pytest.raises(ValueError) as e:
		story_threads.change_thread(C_ARGS)

def test_change_pos_dev_before_opening(monkeypatch, tmp_path):
	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "development", ["0"])

	with pytest.raises(ValueError) as e:
		story_threads.change_thread(C_ARGS)

def test_change_pos_opening_to_ending(monkeypatch, tmp_path):
	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "opening", ["4"])

	with pytest.raises(ValueError) as e:
		story_threads.change_thread(C_ARGS)

def test_change_thread_non_existent(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD_FIRST, f, ensure_ascii=False)

	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "hero on a search")
	monkeypatch.setattr(C_ARGS, "development", ["2", "3"])

	with pytest.raises(ValueError) as e:
		story_threads.change_thread(C_ARGS)

def test_change_thread_open(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD_FIRST, f, ensure_ascii=False)

	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "protagonist feels lonely")
	monkeypatch.setattr(C_ARGS, "ending", ["2", "3"])

	with pytest.raises(ValueError) as e:
		story_threads.change_thread(C_ARGS)

def test_change_thread_not_developed(monkeypatch, tmp_path):
	only_opening_thread = OPEN_THREAD
	monkeypatch.delitem(only_opening_thread, "2")
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(only_opening_thread, f, ensure_ascii=False)

	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "protagonist feels lonely")
	monkeypatch.setattr(C_ARGS, "development", ["2", "1"])

	with pytest.raises(ValueError) as e:
		story_threads.change_thread(C_ARGS)

def test_change_thread_no_event(monkeypatch, tmp_path):
	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "protagonist feels lonely")

	with pytest.raises(ValueError) as e:
		story_threads.change_thread(C_ARGS)

def test_change_too_many_descriptions(monkeypatch, tmp_path):
	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "opening", ["1", "new description", "too_much"])

	with pytest.raises(ValueError) as e:
		story_threads.change_thread(C_ARGS)

def test_change_too_many_indices(monkeypatch, tmp_path):
	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "antagonist in disguise")
	monkeypatch.setattr(C_ARGS, "opening", ["1", "2", "new description"])

	with pytest.raises(ValueError) as e:
		story_threads.change_thread(C_ARGS)

def test_change_non_existent_dev(monkeypatch, tmp_path):
	with open(Path(tmp_path, "runtests.json"), "w") as f:
		json.dump(WHOLE_THREAD_FIRST, f, ensure_ascii=False)

	C_ARGS.path = tmp_path
	monkeypatch.setattr(C_ARGS, "name", "protagonist feels lonely")
	monkeypatch.setattr(C_ARGS, "development", ["hero finds the first clue", "hero finds the last clue"])

	with pytest.raises(ValueError) as e:
		story_threads.change_thread(C_ARGS)


# error cases (change), also checked by argparse:
# two events are passed (currently mutually exclusive)

# test showthread?
# test undo
# test helper functions
