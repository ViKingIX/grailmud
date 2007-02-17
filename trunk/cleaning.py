import os

def get_all_files_from_subdirs(directory):
    for filename in os.listdir(directory):
        if filename != '.svn':
            if os.path.isdir(filename):
                dirname = os.path.join(directory, filename)
                for name in get_all_files_from_subdirs(dirname):
                    yield name
            else:
                yield os.path.join(directory, filename)

def filter_out_trash(files):
    for filename in files:
        if filename.endswith('.pyc'):
            yield filename

def remove_trash(directory):
    for trashname in filter_out_trash(get_all_files_from_subdirs(directory)):
        print 'Removing %s' % trashname
        os.remove(trashname)

