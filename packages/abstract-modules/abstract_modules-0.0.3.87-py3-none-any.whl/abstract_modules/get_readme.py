from abstract_utilities import read_from_file,make_list,os
def get_readme_file_paths(abs_path=None):
    abs_path = abs_path or os.getcwd()
    if os.path.isfile(abs_path):
        abs_path = os.path.dirname(abs_path)
    if os.path.isdir(abs_path):
        abs_dir = abs_path
    pattern = os.path.join(abs_dir, '**', f'README.md')
    readme_file_paths = make_list(glob.glob(pattern, recursive=True) or '')
    return readme_file_paths
def get_readme_path():
    readme_file_paths = get_readme_file_paths()
    for readme_file_path in readme_file_paths:
        if os.path.isfile(readme_file_path):
            return readme_file_path
def get_readme_data(readme_file_path=None,abs_path=None):
    readme_file_path = readme_file_path or get_readme_path(abs_path)
    long_description = ''
    if os.path.isfile(readme_file_path):
        long_description = read_from_file(readme_file_path)
    return long_description
