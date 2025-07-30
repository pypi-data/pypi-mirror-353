from abstract_utilities import *
from abstract_webserver import *

import os,glob,ast,json,runpy,builtins,json,ast,os,glob
from typing import *
def glob_search(directory: str, basename: str, ext: Optional[str] = None) -> List[str]:
    """Recursively search for files matching basename and extension."""
    basenames = make_list(basename)
    exts = make_list(ext or '*')
    found_paths = []
    
    for basename in basenames:
        split_filename, _ = os.path.splitext(basename)
        filename = split_filename or '*'
        for ext in make_list(exts or '*'):
            ext = ext.lstrip('.')
            pattern = os.path.join(directory, '**', f'{filename}.{ext}')
            found_paths.extend(glob.glob(pattern, recursive=True))
    
    return found_paths
def get_synopsis_file_path(module_info,partial_path):
    module_info_dir = module_info.get("module_info_dir")
    module_directory = module_info.get("module_directory")
    dirname = os.path.dirname(partial_path)
    basename = os.path.basename(partial_path)
    filename,ext = os.path.splitext(basename)
    new_dir = os.path.join(dirname,filename)
    paths = new_dir.split('/')[1:]
    full_path = module_info_dir
    for path in paths:
        full_path = os.path.join(full_path,path)
        os.makedirs(full_path,exist_ok=True)
    synopsis_file_path = os.path.join(full_path,'synopsis.txt')
    return synopsis_file_path
def get_complete_synopsis(module_info):
    if not module_info.get('content_synopsis'):
        module_info['content_synopsis'] = {}
    if not module_info['content_synopsis'].get("complete_synopsis"):
        module_info_dir = module_info.get("module_info_dir")
        module_info['content_synopsis']["complete_synopsis"] = os.path.join(module_info_dir,'complete_synopsis.txt')
    complete_synopsis_file_path = module_info['content_synopsis']["complete_synopsis"]
    if not os.path.isfile(complete_synopsis_file_path):
       write_to_file(contents="", file_path = complete_synopsis_file_path)
       save_module_info(module_info)
    return read_from_file(complete_synopsis_file_path)
def save_synopsis_file(module_info,partial_path,content):
    complete_synopsis = get_complete_synopsis(module_info)
    if not module_info['content_synopsis'].get(partial_path):
        synopsis_file_path = get_synopsis_file_path(module_info,partial_path)
        module_info['content_synopsis'][partial_path] = synopsis_file_path
    synopsis_file_path = module_info['content_synopsis'][partial_path]
    if not os.path.isfile(synopsis_file_path):
        write_to_file(contents=content,file_path=synopsis_file_path)
        complete_synopsis_file_path = module_info['content_synopsis']["complete_synopsis"]
        complete_synopsis += f"{content}/n/n"
        write_to_file(contents=complete_synopsis,file_path=complete_synopsis_file_path)
        save_module_info(module_info)
    return complete_synopsis
def resolve_module_path(module: str, base_dir: str) -> Optional[str]:
    """Resolve a module (dotted or relative) to a file or directory path."""
    # Split module into parts, handling leading dots
    parts = module.split('.')
    current_dir = base_dir
    module_parts = []
    
    # Process leading dots for relative imports
    for part in parts:
        if part == '':
            current_dir = os.path.dirname(current_dir)
        else:
            module_parts.append(part)
    
    # Build path for remaining parts
    module_path = os.path.join(current_dir, *module_parts)
    
    # Check if it’s a file
    file_path = f"{module_path}.py"
    if os.path.isfile(file_path):
        return file_path
    
    # Check if it’s a package (directory with __init__.py)
    if os.path.isdir(module_path):
        init_path = os.path.join(module_path, '__init__.py')
        if os.path.isfile(init_path):
            return init_path
    
    return None

def extract_imports(file_path: str) -> List[str]:
    """Extract import statements from a Python file."""
    imports = []
    content = read_from_file(file_path)
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith(('import ', 'from ')):
            parts = line.split()
            if len(parts) > 1:
                # Handle 'import module' or 'from module import ...'
                module = parts[1] if parts[0] == 'import' else parts[1].split('.')[0]
                module = module.split(',')[0].split(' as ')[0]
                imports.append(module)
    return imports

def get_py_script_paths(paths: List[str], module_paths: List[str] = None, imports: List[str] = None) -> Tuple[List[str], List[str]]:
    """Recursively collect module paths and imports from Python files."""
    module_paths = module_paths or []
    imports = imports or []
    paths = make_list(paths)
    
    for path in paths:
        if not os.path.exists(path):
            print(f"Path not found: {path}")
            continue
        
        if os.path.isdir(path):
            # Search for Python files in directory
            py_files = glob_search(path, '*', ext='.py')
            module_paths, imports = get_py_script_paths(py_files, module_paths, imports)
        else:
            # Add the current script to module_paths
            if path.endswith('.py') and path not in module_paths:
                module_paths.append(path)
            
            # Extract imports
            file_imports = extract_imports(path)
            imports.extend(file_imports)
            
            # Handle relative imports (from .module import ...)
            init_dir = os.path.dirname(path)
            content = read_from_file(path)
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('from .'):
                    module = line.split('from .')[-1].split(' ')[0]
                    resolved_path = resolve_module_path(module, init_dir)
                    if resolved_path and resolved_path not in module_paths:
                        module_paths, new_imports = get_py_script_paths([resolved_path], module_paths, imports)
                        imports.extend(new_imports)
    
    return list(set(module_paths)), list(set(imports))
