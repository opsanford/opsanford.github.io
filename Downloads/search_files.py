#!/bin/python3

import os
import sys

keep_open : bool = False
text_file_extensions = ["txt", "html", "py", "csv", "js", "json", "tsv"]

def get_input_prompt(num_non_option_args : int, num_option_args : int):
    if num_non_option_args == 0:
        return "search term (or option): "
    if num_non_option_args == 1:
        return "search directory (defaults to current directory) or option: "
    return "additional option (press enter for no additional option): "

def print_help():
    print("Command usage:")
    print("python .\\search_files.py <search_term> [<directory>] [<options>]")
    print("search_term: the string to be searched in file names")
    print("directory:   path to the directory in which all files and subdirectories shall be searched")
    print("Option '-h': print this help message")
    print("Option '-i': ignore case when searching")
    print("Option '-c': also search for search term within the contents of text files")
    print("             These file extensions count as text files:", text_file_extensions)
    print()
    if keep_open:
        input("Press enter to exit")
    
    
def check_contents(root : str, filename : str, search_term : str, ignore_case : bool) -> bool:
    file_ext = filename.split(".")[-1]
    if not file_ext in text_file_extensions: return False
    search_bytes = search_term.encode("utf-8")
    ignored_length = len(search_bytes) - 1
    filepath = root + os.path.sep + filename
    try:
        with open(filepath, "rb") as file:
            while True:
                contents = file.read(1000)
                if len(contents) <= ignored_length: break
                if ignore_case: contents = contents.lower()
                if search_bytes in contents: return True
                file.seek(file.tell() - ignored_length)
    except:
        print("Error when reading file", filepath)
    return False

def main(args : list[str]):
    if not args:
        args = ["search_files.py"]
    if len(args) == 1:
        num_non_option_args = 0
        print("Usage: python .\\search_files.py <search term> [<directory>] [-c] [-i]")
        print("       python .\\search_files.py -h for help")
        print("Running in interactive mode")
        for i in range(10):
            input_prompt = get_input_prompt(num_non_option_args, i - num_non_option_args)
            arg = input(input_prompt)
            if arg == "" and num_non_option_args >= 2: break
            args.append(arg)
            if arg.startswith("-"):
                if "h" in arg: break
            else:
                num_non_option_args += 1
        global keep_open
        keep_open = True
    
    num_non_option_args = 0
    search_term : str = ""
    search_dir : str = "."
    ignore_case : bool = False
    look_at_contents : bool = False
    
    for i, arg in enumerate(args):
        if i == 0: continue
        if arg.startswith("-"):
            for symbol in arg[1:]:
                if symbol == "h":
                    print_help()
                    return
                if symbol == "i":
                    ignore_case = True
                    continue
                if symbol == "c":
                    look_at_contents = True
                    continue
                print("Error: Unknown option:", symbol)
                return
        else:
            if num_non_option_args == 0:
                search_term = arg
            elif num_non_option_args == 1:
                search_dir = arg
                if not arg: search_dir = "."
            else:
                print("Error: Too many arguments")
                return
            num_non_option_args += 1
    
    if ignore_case:
        search_term = search_term.lower()
    
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if search_term in (file.lower() if ignore_case else file): print(root + os.path.sep + file)
            elif look_at_contents:
                if check_contents(root, file, search_term, ignore_case): print(root + os.path.sep + file)
        for dir in dirs:
            if search_term in (dir.lower() if ignore_case else dir): print(root + os.path.sep + dir + os.path.sep)
    
    print("\nSearch finished")
    if keep_open:
        input("Press enter to exit")
    
if __name__ == "__main__":
    main(sys.argv)
