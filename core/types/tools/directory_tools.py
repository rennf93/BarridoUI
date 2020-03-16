import glob
import os

def remove_hidden_files_names(files_list):
    return filter(files_names_filter, files_list)


def remove_hidden_files(files_list):
    return filter(files_filter, files_list)


def files_filter(file):
    root_strings = ['.', '__']
    for string in root_strings:
        if file.filename.startswith(string):
            return False
    return True


def files_names_filter(file):
    root_strings = ['.', '__']
    for string in root_strings:
        if file.startswith(string):
            return False
    return True


def clean_folder(folder, extension):
    filelist = glob.glob(os.path.join(folder, extension))
    for f in filelist:
        os.remove(f)
