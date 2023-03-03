import argparse

import story_threads

### parse input and call functions ###

parser = argparse.ArgumentParser(prog = "story-threads", description = "Show all story threads in order")
parser.add_argument("story", type=str, help="the story name (acts as file name to store the data threads)")
parser.add_argument("-p", "--path", type=str, default="", help="the path to the story file")
parser.add_argument("-c", "--show_connections", action="store_true", help="show all connections to the main story thread")
subparsers = parser.add_subparsers(help="the program mode")
parser_add = subparsers.add_parser("add", help="add a new story thread or add a new part to an existing story thread")
parser_add.add_argument("names", type=str, nargs="+", help="the thread name (corresponds to the text of the first event) and the texts for the remaining events, if any")
parser_add.add_argument("-i", "--indices", type=int, nargs="+", required=True, help="the indices of the events on which to open, develop and/or close the thread")
parser_add.add_argument("-c", "--close", action="store_true", help="close the story thread with the last given index (if not set, every event after the opening is considered a development)")
parser_add.set_defaults(func=story_threads.add_thread)
parser_rm = subparsers.add_parser("remove", aliases=["rm"], help="remove a story thread")
parser_rm.add_argument("name", type=str, help="the name of the thread to be removed")
parser_rm.add_argument("-d", "--development", type=str, nargs="+", help="remove only the given thread development(s)")
parser_rm.add_argument("-e", "--ending", action="store_true", help="remove only the closing of the thread (i.e. open it again)")
parser_rm.set_defaults(func=story_threads.remove_thread)
parser_change = subparsers.add_parser("change", help="change the position of a story thread's opening and/or closing")
parser_change.add_argument("name", type=str, help="the name of the thread to be changed")
parser_change.add_argument("-o", "--opening", type=str, nargs="+", help="change the opening index and/or description of the thread")
parser_change.add_argument("-d", "--development", type=str, nargs="+", help="change thread development indices and/or descriptions")
parser_change.add_argument("-e", "--ending", type=str, nargs="+", help="change the closing index and/or description of the thread")
parser_change.set_defaults(func=story_threads.change_thread)
parser_list = subparsers.add_parser("show", help="show all story threads")
parser_list.set_defaults(func=story_threads.show_threads)
args = parser.parse_args()
args.func(args)
