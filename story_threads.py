import argparse
import json
from pathlib import Path
from enum import Enum


### helper functions ###

class EVENT(str, Enum):
	"""
	Define the events of the story thread.
	"""
	OPENING = "open"
	CLOSING = "close"
	DEVELOPMENT = "develop"

def retrieve_storythreads(story, path):
	"""
	Load the story threads from the json file if it exists.

	The story threads are dictionaries (to be able to identify them by
	name) stored in a list (to order them by index). To load them from
	a json file, the outer dictionary with the list indices as keys is
	converted back to the list of dictionaries.

	Args:
		story: The name of the story that corresponds to the json file
			name.
		path: The path to the json file.

	Return:
		thread_list: The list of dictionaries that represent story
			threads.
	"""
	# the threadlist is a list of dictionaries, stored as a json file
	storythread_file = Path(path, story + ".json")
	thread_list = []
	try:
		with open(storythread_file, "r") as f:
			thread_dict = json.load(f)
		sorted_keys = [int(k) for k in thread_dict.keys()]
		sorted_keys.sort()
		thread_list = [thread_dict[str(k)] for k in sorted_keys]
	except (FileNotFoundError, json.decoder.JSONDecodeError):
		pass
	return thread_list

def store_storythreads(story, path, thread_list):
	"""
	Store the story threads as a json file.

	The story threads are dictionaries (to be able to identify them by
	name) stored in a list (to order them by index). To store them as
	a json file, the list is converted to a dictionary with the indices
	as keys.

	Args:
		story: The name of the story that corresponds to the json file
			name.
		path: The path to the json file.
		thread_list: The list of dictionaries that represent story
			threads.
	"""
	storythread_file = Path(path, story + ".json")
	storythread_file.parent.mkdir(parents=True, exist_ok=True)
	#json.dumps(vars(new_StoryThread))
	with open(storythread_file, "w") as f:
		json.dump({i: el for i, el in enumerate(thread_list)}, f, ensure_ascii=False)

def thread_is_closed(thread_list, thread_id):
	"""
	Find out if a given thread has been closed.

	A non-existing thread is not closed.

	Args:
		thread_list: The list of dictionaries that represent story
			threads.
		thread_id: The id/name of the thread to check.

	Return:
		Boolean: True, if the thread exists and has been closed, else
			False
	"""
	if thread_id not in [next(iter(el.keys())) for el in thread_list]:
		return False
	thread_ids = [next(iter(el.keys())) for el in thread_list]
	index_last_entry = len(thread_ids) - 1 - list(reversed(thread_ids)).index(thread_id)
	if thread_list[index_last_entry][thread_id]["event"] == EVENT.CLOSING:
		return True
	return False

def thread_events_are_new(thread_list, thread_id, descriptions):
	"""
	Check if the event descriptions are different from those of a given
	thread.

	Args:
		thread_list: The list of dictionaries that represent story
			threads.
		thread_id: The id/name of the thread to check.
		descriptions: The list of descriptions to check against the
			given thread's descriptions.

	Return:
		Boolean: True, if the descriptions differ, else False
	"""
	# gather all elements of the thread
	thread_descriptions = set()
	for el in thread_list:
		name = next(iter(el.keys()))
		if name == thread_id:
			thread_descriptions.add(el[name]["description"])

	# check if the given description(s) already exist(s)
	return thread_descriptions.isdisjoint(descriptions)


### display threads ###

class STATE(str, Enum):
	"""
	Define the elements of the story thread representation.
	"""
	OPEN = "│  "
	OPENING = "├─ "
	CLOSING = "┘  "
	CLOSED = "   "
	CLOSINGNEIGHBOR = "───"
	OPENINGNEIGHBOR = "── "
	MERGENEIGHBOR = "├──"
	NOTCLOSED = "┊  "
#└─
#─┤

def show_threads(args):
	"""
	Show a story's threads.

	Prints the story threads stored in the json file.

	Args:
		args: The arguments passed to the program by the user.
	"""
	thread_list = retrieve_storythreads(args.story, args.path)
	if thread_list == []:
		print("There is no story thread to show yet.")
		return
	spacing = len(str(len(thread_list)*2)) # max length of line numbers
	print(f"{(spacing) * ' '} {args.story}")
	print(f"{(spacing) * ' '} │")
	open_list = []
	for t, current_thread in enumerate(thread_list):
		current_thread_name = next(iter(current_thread.keys()))
		spacing_offset = (spacing - len(str(t))) * ' '
		# add an opening thread to the list of open threads
		if not current_thread_name in open_list:
			open_list.append(current_thread_name)
		# traverse the list in reverse to handle right neighbor states
		neighbor_is_opening = False
		neighbor_is_closing = False
		line = ""
		for i, thread in enumerate(reversed(open_list)):
			# if the thread is the currently opened, developed or closed
			# thread
			if thread == current_thread_name:
				if current_thread[current_thread_name]["event"] == EVENT.OPENING:
					if not current_thread_name == current_thread[current_thread_name]["description"]:
						if thread_is_closed(thread_list, current_thread_name):
							line = current_thread_name + ": " + current_thread[current_thread_name]["description"] + line
						else:
							line = "\033[1m" + current_thread_name + "\033[0m: " + current_thread[current_thread_name]["description"] + line
					else:
						line = current_thread[current_thread_name]["description"] + line
					neighbor_is_opening = True
				else:
					if current_thread[current_thread_name]["event"] == EVENT.DEVELOPMENT:
						current_state = STATE.OPEN
					else:
						current_state = STATE.CLOSING
						neighbor_is_closing = True
					desc_len = len(current_thread[current_thread_name]["description"]) + 1
					#print(desc_len, line, len(line), line[desc_len:])
					if desc_len <= len(current_state):
						line = current_state + line
					elif desc_len >= len(line):
						line = f"{current_state[0]}{current_thread[current_thread_name]['description']}"
					else:
						line = f"{current_state[0]}{current_thread[current_thread_name]['description']}{line[desc_len:]}"
			# if the thread has been closed
			elif thread is None:
				if neighbor_is_closing or neighbor_is_opening:
					if neighbor_is_opening and list(reversed(open_list))[i-1] == current_thread_name:
						line = STATE.OPENINGNEIGHBOR + line
					else:
						line = STATE.CLOSINGNEIGHBOR + line
				else:
					line = STATE.CLOSED + line
			# if the thread is open
			else:
				if neighbor_is_opening:
					if list(reversed(open_list))[i-1] is None:
						line = STATE.MERGENEIGHBOR + line
					else:
						line = STATE.OPENING + line
					if not args.show_connections:
						neighbor_is_opening = False
				elif neighbor_is_closing:
					line = STATE.MERGENEIGHBOR + line
					if not args.show_connections:
						neighbor_is_closing = False
				else:
					line = STATE.OPEN + line

		# add main story thread
		if neighbor_is_opening:
			if len(open_list) >= 1 or open_list[1] is None:
				line = STATE.MERGENEIGHBOR + line
			else:
				line = STATE.OPENING + line
		elif neighbor_is_closing:
			line = STATE.MERGENEIGHBOR + line
		else:
			line = STATE.OPEN + line

		# add the line number
		line = f"{spacing_offset}{t} " + line
		print(line)

		# remove a closing thread from the list of open threads
		if current_thread[current_thread_name]["event"] == EVENT.CLOSING:
			open_list[open_list.index(current_thread_name)] = None

	# indicate open threads
	line = f"{(spacing) * ' '} {STATE.NOTCLOSED}"
	for thread in open_list:
		if thread is not None:
			line = line + STATE.NOTCLOSED
		else:
			line = line + STATE.CLOSED
	print(line)

	print(f"Number of threads: {len(set([next(iter(key)) for key in thread_list]))} + 1 (main thread)")
	print(f"Number of open threads: {len(open_list) - open_list.count(None)} + 1 (main thread)")

# more sophisticated sample (with new threads claiming empty columns):
#
#story (main thread)
#│
#├─ thread a (e.g. main thread first book)
#│  ├─ thread b
#│  │  ├─ thread c
#│  │  │  ├─ thread d
#│  ├──┘  │  │
#│  ├─ thread b2
#│  │  ├──┘  │
#├──┴──┘     │   (probably don't allow two to end at the same time)
#┊           ┊


def undo(args):
	"""
	Undo the last action

	This is done by loading the cached thread_list from file.

	Args:
		args: The arguments passed to the program by the user.
	"""
	thread_list = retrieve_storythreads(f".{args.story}", args.path)
	store_storythreads(args.story, args.path, thread_list)

	# show state
	show_threads(args)


### manipulate threads (add, remove and change) ###

def add_thread(args, nocache=False):
	"""
	Add a story thread or parts of a story thread.

	If the name of the story thread does not exist yet: Add the story
	thread to the json at the given index.
	The first of the names acts as id and opening descriptions, if one
	less index than name is given.
	If only the opening or the opening and a development (or
	developments) are given, the story thread is left open. If a closing
	flag is given and the thread is open, the last event closes the
	thread.
	If the name of the story thread exists and the closing flag is not
	set: Develop the respective story thread and store it in the json.
	If the name of the story thread exists and the close flag is set:
	Develop the respective story thread if more than one event is given
	and close the story thread with the last event. Then, store it in
	the json.

	Args:
		args: The arguments passed to the program by the user.
		nocache (Boolean): A flag to determine whether the current
			thread will be cached before changes are applied. The
			default is to cache the thread (False).

	Raises:
		ValueError: If
			- no name is given for the thread (checked by argparse)
			- no indices are given for the thread (checked by argparse)
			- the thread contains events with the given descriptions
			- descriptions are missing for opening or developments
			- the order of opening, developments, closing is wrong
	"""
	if not args.names:
		raise ValueError("You need to pass at least one event name to act as identifier for the story thread")
	if not args.indices:
		raise ValueError("You need to pass indices to add something")
	if args.close and not all(args.indices[-1] >= args.indices[i+1] for i in range(len(args.indices) - 1)):
		raise ValueError("The story thread must close after it opens or develops")

	# load the threads
	thread_list = retrieve_storythreads(args.story, args.path)
	events = args.names.copy()
	thread_id = args.names[0]
	thread_is_new = thread_id not in [next(iter(el.keys())) for el in thread_list]

	# remove id if the first name may be the id
	if thread_is_new:
		if len(args.names) + 1 == len(args.indices) and args.close:
			pass
		elif len(args.names) == len(args.indices) + 1:
			events.pop(0)
		elif len(args.names) == len(args.indices) and not args.close:
			pass
		elif len(args.names) == len(args.indices) and args.close:
			# only unclear state, first could be id or ending could have
			# no description
			pass
			#events.pop(0)
		else:
			raise ValueError("Missing description. Every event except of the closing of a story thread needs a description")
	else:
		events.pop(0)

	#assert len(events) <= len(args.indices)

	if thread_is_new and not all(args.indices[0] <= args.indices[i+1] for i in range(len(args.indices) - 1)):
		raise ValueError("The story thread must open before it can develop or close")
	if not thread_events_are_new(thread_list, thread_id, events):
		raise ValueError("The story thread already contains events with these descriptions")
	if args.close and thread_is_closed(thread_list, thread_id):
		raise ValueError("Cannot close a closed thread")

	if not nocache:
		store_storythreads(f".{args.story}", args.path, thread_list)

	# create a new thread
	shift_indices = 0
	for i, index in enumerate(args.indices):
		description = ""
		# closings can be without description
		try:
			description = events.pop(0)
		except IndexError:
			pass
		current_event = EVENT.DEVELOPMENT
		# if the thread is new, add an opening
		if thread_id not in [next(iter(el.keys())) for el in thread_list]:
			current_event = EVENT.OPENING
		# if the thread is to be closed, close it
		elif i == len(args.indices)-1 and args.close and not thread_is_closed(thread_list, thread_id):
			current_event = EVENT.CLOSING
		# add the thread event
		thread_list.insert(int(index)+shift_indices, {thread_id: {"event": current_event, "description": description}})
		# because a thread has been added, in order to keep the
		# indices correct, increment the index
		shift_indices += 1

	# store changes
	store_storythreads(args.story, args.path, thread_list)

	# show changes
	show_threads(args)

def remove_thread(args, noshow=False, nocache=False):
	"""
	Remove a story thread or parts of a story thread.

	If only the name of the story thread is given: Remove the whole
	story thread from the json. If the ending or the development is
	given but not the opening, remove the respective parts from the
	story thread.

	Args:
		args: The arguments passed to the program by the user.
		noshow (Boolean): A flag to show or not show the threads. The
			default is to show them (False).
		nocache (Boolean): A flag to determine whether the current
			thread will be cached before changes are applied. The
			default is to cache the thread (False).

	Raises:
		ValueError: If
			- the given story thread does not exist
			- the thread is to be opened but is already open
	"""
	thread_list = retrieve_storythreads(args.story, args.path)
	thread_ids = [next(iter(el.keys())) for el in thread_list]

	if args.name not in thread_ids:
		raise ValueError("The story thread with the given name does not exist and cannot be removed")
	if args.ending and not thread_is_closed(thread_list, args.name):
		raise ValueError("The story thread is already open")

	if not nocache:
		store_storythreads(f".{args.story}", args.path, thread_list)

	if args.ending:
		# remove only closing (i.e. open again)
		thread_list.pop(len(thread_ids) - 1 - list(reversed(thread_ids)).index(args.name))
	if args.development:
		# remove only specified developments
		indices = []
		descriptions = []
		for el in args.development:
			try:
				indices.append(int(el))
			except ValueError:
				descriptions.append(el)
		for i,t in enumerate(thread_list):
			key = next(iter(t.keys()))
			if t[key]["event"] == EVENT.DEVELOPMENT and t[key]["description"] in descriptions:
				indices.append(i)
		removed = 0
		indices.sort()
		for i in indices:
			if thread_ids[i] == args.name:
				if thread_list[i-removed][next(iter(thread_list[i-removed].keys()))]["event"] == "develop":
					thread_list.pop(i-removed)
					removed += 1
				else:
					print(f"Did not remove thread development at index {i} as it is not a development.")
			else:
				print(f"Did not remove thread development at index {i} as it belongs to a different thread.")
		if removed == 0:
			print(f"There was nothing to remove.")
	if not args.ending and not args.development:
		# remove whole thread
		while(args.name in thread_ids):
			thread_list.pop(thread_ids.index(args.name))
			thread_ids.remove(args.name)
	store_storythreads(args.story, args.path, thread_list)

	# show changes
	if not noshow:
		show_threads(args)

def change_thread(args):
	"""
	Change a story thread's opening, development and/or closing indices.

	Move the indices of the story thread events by removing and adding
	them to the indices provided by the user and storing the changes in
	the json.
	Note: Currently, only one event can be changed at a time.

	Args:
		args: The arguments passed to the program by the user.

	Raises:
		ValueError: If
			- the given story thread does not exist
			- no thread event to change is given
			- more than one index or description is given per event
			- the development to be changed does not exist
			- the order of opening, developments, closing is wrong
	"""
	if not args.opening and not args.ending and not args.development:
		ValueError("No thread event specified for change")
	if len(args.opening) > 2 or len(args.ending) > 2 or len(args.development) > 3:
		ValueError("You can only change one index and description per event")

	thread_list = retrieve_storythreads(args.story, args.path)
	thread_ids = [next(iter(el.keys())) for el in thread_list]

	if args.name not in thread_ids:
		raise ValueError("The story thread with the given name does not exist and cannot be changed")
	if args.ending and not thread_is_closed(thread_list, args.name):
		raise ValueError("The story thread is not closed. The ending cannot be changed.")

	store_storythreads(f".{args.story}", args.path, thread_list) # cache

	# get the current thread
	dev_index = -1
	current_indices = []
	current_descriptions = []
	current_close = False
	for i,el in enumerate(thread_list):
		name = next(iter(el.keys()))
		if name == args.name:
			current_indices.append(i)
			try:
				current_descriptions.append(el[name]["description"])
			except IndexError:
				pass
			if args.development and el[name]["event"] == EVENT.DEVELOPMENT and (str(i) == args.development[0] or el[name]["description"] == args.development[0]):
				dev_index = len(current_indices) - 1
			if el[name]["event"] == EVENT.CLOSING:
				current_close = True

	# apply changes
	if args.opening:
		for el in args.opening:
			try:
				current_indices[0] = int(el)
			except ValueError:
				current_descriptions[0] = el
		if not all(current_indices[0] <= i for i in current_indices[1:]):
			raise ValueError("The story thread must open before it can develop or close")
	if args.development:
		if dev_index < 0:
			raise ValueError(f"The given development index or description does not match a known development.")
		for el in args.development:
			try:
				current_indices[dev_index] = int(el)
			except ValueError:
				current_descriptions[dev_index] = el
		if current_indices[0] > current_indices[dev_index]:
			raise ValueError(f"The story thread cannot develop before it opens.")
	if args.ending:
		for el in args.ending:
			try:
				current_indices[-1] = int(el)
			except ValueError:
				current_descriptions[-1] = el
		#current_descriptions.insert(0, args.name)
		if not all(current_indices[-1] >= i for i in current_indices[:-1]):
			raise ValueError("The story thread must close after it opens or develops")

	# adjust indices for removed elements
	for i in range(len(current_indices)):
		current_indices[i] -= i

	# add the id
	current_descriptions.insert(0, args.name)

	params = argparse.Namespace(
		story = args.story,
		path = args.path,
		show_connections = args.show_connections,
		names = current_descriptions,
		indices = current_indices,
		close = current_close
	)

	# remove old thread, create and store changed thread
	remove_thread(argparse.Namespace(story=args.story, path=args.path, show_connections=args.show_connections, name=args.name, ending=False, development=""), noshow=True, nocache=True)
	add_thread(params, nocache=True)
