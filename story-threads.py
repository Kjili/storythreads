import argparse
import json
from pathlib import Path
from enum import Enum


### helper functions ###

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
		thread_list = list(thread_dict.values())
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
		spacing_offset = (spacing - len(str(t))) * ' '
		current_is_opening = False
		# add an opening thread to the list of open threads
		if not current_thread in open_list:
			open_list.append(current_thread)
			current_is_opening = True
		# traverse the list in reverse to handle right neighbor states
		neighbor_is_opening = False
		neighbor_is_closing = False
		line = ""
		for i, thread in enumerate(reversed(open_list)):
			# if the thread is the currently opened or closed thread
			if thread == current_thread:
				if current_is_opening:
					line = current_thread + line
					neighbor_is_opening = True
				else:
					line = STATE.CLOSING + line
					neighbor_is_closing = True
			# if the thread has been closed
			elif thread is None:
				if neighbor_is_closing or neighbor_is_opening:
					if neighbor_is_opening and list(reversed(open_list))[i-1] == current_thread:
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
		if not current_is_opening:
			open_list[open_list.index(current_thread)] = None

	# indicate open threads
	line = f"{(spacing) * ' '} {STATE.NOTCLOSED}"
	for thread in open_list:
		if thread is not None:
			line = line + STATE.NOTCLOSED
		else:
			line = line + STATE.CLOSED
	print(line)

	print(f"Number of threads: {len(set(thread_list))} + 1 (main thread)")
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


### manipulate threads (add, remove and change) ###

def add_thread(args):
	"""
	Add a story thread or parts of a story thread.

	If the name of the story thread does not exist yet: Add the story
	thread to the json at the given index. If only the opening or the
	opening and a development is given (TODO), the story thread is left open.
	If the name of the story thread exists and only one value is given:
	Close the respective story thread and store it in the json. (TODO)
	If the name of the story thread exists and a development is given:
	Add the development to the story thread. (TODO)

	Args:
		args: The arguments passed to the program by the user.

	Raises:
		parser.error: If the ... (TODO)
	"""
	if args.opened < 0:
		raise parser.error("To open a story thread, you must provide a valid index")
	if args.closed <= args.opened and args.closed >= 0:
		raise parser.error("The story thread must close after it opens, not before")
	thread_list = retrieve_storythreads(args.story, args.path)
	if args.name in thread_list:
		raise parser.error("This story thread already exists and cannot be opened again")

	# create and store new threads
	thread_list.insert(args.opened, args.name)
	if args.closed >= 0:
		# because a thread has been added, in order to remove it at the
		# prior index, need to add + 1 to the closing index
		thread_list.insert(args.closed + 1, args.name)
	store_storythreads(args.story, args.path, thread_list)

	# show changes
	show_threads(args)

def remove_thread(args):
	"""
	Remove a story thread or parts of a story thread.

	If only the name of the story thread is given: Remove the whole
	story thread from the json. If the ending or the development (TODO) is
	given but not the opening, remove the respective parts from the
	story thread.

	Args:
		args: The arguments passed to the program by the user.

	Raises:
		parser.error: If the ... (TODO)
	"""
	thread_list = retrieve_storythreads(args.story, args.path)
	if args.name not in thread_list:
		raise parser.error("The story thread with the given name does not exist and cannot be removed")
	if args.ending and thread_list.count(args.name) <= 1:
		raise parser.error("The story thread is already open")

	if args.ending:
		# remove only closing (i.e. open again)
		thread_list.pop(len(thread_list) - 1 - list(reversed(thread_list)).index(args.name))
	else:
		# remove whole thread
		while(args.name in thread_list):
			thread_list.remove(args.name)
	store_storythreads(args.story, args.path, thread_list)

	# show changes
	show_threads(args)

def close_thread(args):
	# TODO remove this as it will be replaced by the new closing functionality of add_thread
	if args.closed <= 0:
		raise parser.error("To close a story thread, you must provide a valid index")
	thread_list = retrieve_storythreads(args.story, args.path)
	if args.name not in thread_list:
		raise parser.error("The story thread with the given name does not exist and cannot be closed")
	if thread_list.count(args.name) > 1:
		raise parser.error("The story thread with the given name has already been closed")
	if args.closed <= thread_list.index(args.name):
		raise parser.error("The story thread must close after it opens, not before")

	# create and store new threads
	thread_list.insert(args.closed, args.name)
	store_storythreads(args.story, args.path, thread_list)

	# show changes
	show_threads(args)

def change_thread(args):
	"""
	Change a story thread's opening, development (TODO) and/or closing indices.

	Move the indices of the story thread events by removing and adding
	them to the indices provided by the user and storing the changes in
	the json.

	Args:
		args: The arguments passed to the program by the user.

	Raises:
		parser.error: If the ... (TODO)
	"""
	if not args.opening and not args.ending:
		parser.error("Neither opening nor ending of thread specified for change")
	thread_list = retrieve_storythreads(args.story, args.path)
	if args.name not in thread_list:
		raise parser.error("The story thread with the given name does not exist and cannot be changed")
	if thread_list.count(args.name) <= 1 and args.ending:
		raise parser.error("The story thread with the given name has not been closed yet")
	index_last_occurence = len(thread_list) - 1 - list(reversed(thread_list)).index(args.name)
	if (args.opening and args.ending and args.opening > args.ending or
		args.opening and args.opening > index_last_occurence or
		args.ending and thread_list.index(args.name) >= args.ending):
		raise parser.error("The story thread must open before it is closed")

	# remove old threads, create and store new threads
	if args.opening:
		thread_list.remove(args.name)
		thread_list.insert(args.opening, args.name)
	if args.ending:
		thread_list.pop(index_last_occurence)
		thread_list.insert(args.ending, args.name)
	store_storythreads(args.story, args.path, thread_list)

	# show changes
	show_threads(args)


### parse input and call functions ###

parser = argparse.ArgumentParser(prog = "story-threads", description = "Show all story threads in order")
parser.add_argument("story", type=str, help="the story name (acts as file name to store the data threads)")
parser.add_argument("-p", "--path", type=str, default="", help="the path to the story file")
parser.add_argument("-c", "--show_connections", action="store_true", help="show all connections to the main story thread")
subparsers = parser.add_subparsers(help="the program mode")
parser_add = subparsers.add_parser("add", help="add a new story thread")
parser_add.add_argument("name", type=str, help="the thread name")
parser_add.add_argument("opened", type=int, help="the index on which to open the thread")
parser_add.add_argument("-c", "--closed", type=int, default=-1, help="the index on which the thread is closed (corresponds to the index before adding the new thread)")
parser_add.set_defaults(func=add_thread)
parser_end = subparsers.add_parser("end", help="close a story thread")
parser_end.add_argument("name", type=str, help="the thread name")
parser_end.add_argument("closed", type=int, help="the index on which to close the thread")
parser_end.set_defaults(func=close_thread)
parser_rm = subparsers.add_parser("remove", aliases=["rm"], help="remove a story thread")
parser_rm.add_argument("name", type=str, help="the name of the thread to be removed")
parser_rm.add_argument("-e", "--ending", action="store_true", help="remove only the closing of the thread (i.e. open it again)")
parser_rm.set_defaults(func=remove_thread)
parser_change = subparsers.add_parser("change", help="change the position of a story thread's opening and/or closing")
parser_change.add_argument("name", type=str, help="the name of the thread to be removed")
parser_change.add_argument("-o", "--opening", type=int, help="change the opening index of the thread")
parser_change.add_argument("-e", "--ending", type=int, help="change the closing index of the thread")
parser_change.set_defaults(func=change_thread)
parser_list = subparsers.add_parser("show", help="show all story threads")
parser_list.set_defaults(func=show_threads)
args = parser.parse_args()
args.func(args)
