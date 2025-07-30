from abstract_utilities import *
from abstract_webserver import *
from abstract_ai import make_general_query
import os,glob,ast,json,runpy,builtins,json,ast,os,glob
from read_me_prompt import get_readme_prompt
from typing import *
AVOID_LIST ={"california_municipalities.py":"address,zipcoode,state,county information in jsonm format as data for the module"}
def safe_parse_json_from_content(content_list):
    """
    Attempts to extract and parse the last item from a content list as JSON.
    Handles common issues like single quotes or bad escaping.
    """
    if not content_list:
        return None

    raw = content_list[-1]
    if isinstance(raw,dict):
        return raw
    # First, try to fix common JSON issues (like single quotes)
    fixed_json = raw.replace("'", '"')
    
    try:
        # Try normal JSON loading
        return json.loads(fixed_json)
    except json.JSONDecodeError:
        try:
            # Try Python literal eval (safe-ish for well-formed dicts)
            return ast.literal_eval(raw)
        except Exception as e:
            print(f"❌ Failed to parse content: {e}")
            return None
def make_list(item) -> List[str]:
    """Convert item to a list if it’s not already."""
    return item if isinstance(item, list) else [item]

def read_from_file(file_path: str) -> str:
    """Read content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""
def extract_setup_metadata(setup_file: str) -> Dict[str, Any]:
    """Extract metadata from a setup.py file using AST parsing."""
    metadata = {}
    content = read_from_file(setup_file)
    if not content:
        return metadata
    
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'setup':
                for keyword in node.keywords:
                    key = keyword.arg
                    value = None
                    if isinstance(keyword.value, ast.Str):
                        value = keyword.value.s
                    elif isinstance(keyword.value, ast.List):
                        value = [elt.s for elt in keyword.value.elts if isinstance(elt, ast.Str)]
                    elif isinstance(keyword.value, ast.Num):
                        value = keyword.value.n
                    elif isinstance(keyword.value, ast.Name):
                        value = keyword.value.id
                    if value is not None:
                        metadata[key] = value
                break
    except Exception as e:
        print(f"Error parsing {setup_file}: {e}")
    
    return metadata
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

def find_spec_dir(substr: str, directory: str) -> str:
    """Find a directory containing the substring, default to directory."""
    for root, dirs, _ in os.walk(directory):
        for d in dirs:
            if substr in d:
                return os.path.join(root, d)
    return directory

def save_module_info(module_info):
    info_file_path = module_info.get('info_file_path')
    safe_dump_to_file(data=module_info,file_path=info_file_path)
def extract_setup_metadata(setup_py_path):
    metadata = {}

    def fake_setup(**kwargs):
        metadata.update(kwargs)

    # Patch setuptools.setup
    import setuptools
    setuptools.setup = fake_setup

    # Patch open() to return empty string if README.md doesn't exist
    original_open = builtins.open

    def safe_open(file, mode='r', *args, **kwargs):
        if os.path.basename(file).lower() == 'readme.md' and 'r' in mode:
            try:
                return original_open(file, mode, *args, **kwargs)
            except FileNotFoundError:
                import io
                return io.StringIO("")  # return empty content if README.md not found
        return original_open(file, mode, *args, **kwargs)

    builtins.open = safe_open

    try:
        runpy.run_path(setup_py_path, run_name="__main__")
    finally:
        builtins.open = original_open  # Restore original open()

    return metadata
def generate_description_from_metadata(meta):
    name = meta.get("name", "Unnamed Package")
    version = meta.get("version", "0.0.0")
    description = meta.get("description", "")
    author = meta.get("author", "Unknown Author")
    email = meta.get("author_email", "")
    license_ = meta.get("license", "Unknown License")
    classifiers = meta.get("classifiers", [])
    requires = meta.get("install_requires", [])
    entry_points = meta.get("entry_points", {}).get("console_scripts", [])

    summary = f"📦 **{name}** v{version}\n"
    if description:
        summary += f"> {description.strip()}\n\n"
    summary += f"👤 Author: {author}"
    if email:
        summary += f" ({email})"
    summary += "\n"

    summary += f"🪪 License: {license_}\n"

    if classifiers:
        summary += "\n🏷️ Classifiers:\n"
        for cls in classifiers:
            summary += f"  - {cls}\n"

    if requires:
        summary += "\n📦 Dependencies:\n"
        for dep in requires:
            summary += f"  - {dep}\n"

    if entry_points:
        summary += "\n🧩 Entry Points:\n"
        for ep in entry_points:
            summary += f"  - {ep}\n"

    return summary.strip()
def set_value_by_path(obj, path, new_value):
    """Set a value in a nested dict/list given a path like [0, 'response', 'choices', 0, 'message', 'content']"""
    current = obj
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = new_value
    return obj
def get_api_response(module_info,partial_path):
    path_to_key = [partial_path]
    dict_obj = module_info.get(partial_path)
    content = None
    if dict_obj:
        content = get_any_value(dict_obj[0],'content')
        if content and isinstance(content,list) and len(content)>0:
            content = content[-1]
    return content
def update_json_data(module_info, partial_path,dict_obj=None):
    path_to_key = [partial_path]

    # Get the original dict list under the partial path
    dict_obj = dict_obj or module_info.get(partial_path)
    if not dict_obj or not isinstance(dict_obj, list):
        print(f"❌ No valid content under path: {partial_path}")
        return module_info

    # Get the original content field
    content = get_any_value(dict_obj[0], 'content')

    # Find all paths to 'content'
    paths_to_key = find_paths_to_key(dict_obj, 'content')
    if paths_to_key and isinstance(paths_to_key, list) and len(paths_to_key) > 0:
        # Assume last one is most relevant
        paths_to_key = paths_to_key[-1]

    path_to_key += paths_to_key  # Final full key path

    # Parse the content list into a JSON object
    if not isinstance(content,dict):
        parsed = safe_parse_json_from_content(content)
        if not parsed:
            print("❌ Failed to parse new JSON content.")
            return module_info
    else:
        parsed = content
        # Update the nested value using our set_value_by_path helper
    set_value_by_path(module_info, path_to_key, parsed)
    save_module_info(module_info)
    return module_info
def get_partial_path(module_info,module_path):
    module_directory = module_info.get("module_directory")
    src_dir = find_spec_dir('src', module_directory)
    if not module_info.get("partial_paths"):
        module_info["partial_paths"] = []
    module_paths = module_info.get("module_paths")
    partial_path = module_path.replace(src_dir,'src')
    if partial_path not in module_info["partial_paths"]:
        module_info["partial_paths"].append(partial_path)
    return module_info,partial_path
def parse_api_resposes(module_info,info_file_path):
    partial_paths = module_info.get("partial_paths")
    for partial_path in partial_paths:
        update_json_data(module_info, partial_path)
    save_module_info(module_info)
def get_partial_descriptions(module_info):
    partial_paths = module_info.get("partial_paths")
    for partial_path in partial_paths:
        update_json_data(module_info, partial_path)
        json_content = get_api_response(module_info,partial_path)
        if json_content:
            if not module_info.get('content_synopsis'):
                module_info['content_synopsis'] = {"complete_synopsis":""}
            if not module_info['content_synopsis'].get(partial_path):
                if isinstance(json_content,str):
                    api_response = eatAll(json_content.split("\'api_response\':")[1].split('generate_title')[0],['"',"'",',',' ','//','\n',':',"}","{"])
                    generate_title = eatAll(json_content.split("\'generate_title\':")[1].split("\'}'")[0],['"',"'",',',' ','//','\n',':',"}","{"])
                    json_content = {"api_response":api_response,"generate_title":generate_title}
                    try:
                        module_info[partial_path][0]["response"]["choices"][0]["message"]["content"] = json_content
                    except Exception as e:
                        print(f"{e}")
                 
                api_response = json_content.get('api_response')
                generate_title = json_content.get('generate_title') 
                description = f" in the script: {partial_path}\n dubbed with the title: {generate_title}\n was described as: {api_response}\n\n"
                save_synopsis_file(module_info,partial_path,description)
        
    return get_complete_synopsis(module_info)

def make_api_call(**kwargs):
    response = ''
    try:
        response = make_general_query(**kwargs)
    except Exception as e:
        print(f"{e}")
        
    return response
def main(module_directories: List[str]):
    """Process module directories and map modules and imports."""
    for module_directory in make_list(module_directories):
        # Find src directory or use root
        src_dir = find_spec_dir('src', module_directory)
        if not os.path.exists(src_dir):
            print(f"Source directory not found: {src_dir}")
            continue
        
        # Create module_info directory
        module_info_dir = os.path.join(module_directory, 'module_info', 'descriptions')
        os.makedirs(module_info_dir, exist_ok=True)
        info_file_path = os.path.join(module_info_dir, 'module_info.json')
        read_me_response_path = os.path.join(module_info_dir, 'read_me_response.json')
        
        if os.path.isfile(info_file_path):
            module_info = safe_load_from_file(info_file_path)
        if not module_info.get('info_file_path'):
            module_info['info_file_path'] = info_file_path
            save_module_info(module_info)
        if not module_info.get("module_info_dir"):
            module_info["module_info_dir"]=module_info_dir
            save_module_info(module_info)
        if not module_info.get("read_me_response_path"):
            module_info["read_me_response_path"]=read_me_response_path
            save_module_info(module_info)
        if not  module_info.get('module_paths'):
            setup_py_path = os.path.join(module_directory,'setup.py')
            
            # Find all Python files, prioritizing __init__.py
            init_paths = glob_search(src_dir, '__init__', ext='.py')
            all_py_files = glob_search(src_dir, '*', ext='.py')
            module_paths, imports = get_py_script_paths(init_paths + all_py_files)
            meta_data = extract_setup_metadata(setup_py_path)
            # Print results
            print(f"\nModule Directory: {module_directory}")
            print("Imports:", sorted(imports))
            print("Module Paths:", sorted(module_paths))
            #print("Meta Data:",meta_data)
            module_info["module_directory"]=module_directory
            module_info["module_paths"]=sorted(module_paths)
            module_info["Imports"]=sorted(imports)
            module_info["meta_data"]=meta_data
            module_info["info_file_path"]=info_file_path
            module_info["module_info_dir"]=module_info_dir
            module_info["info_file_path"]=info_file_path
            module_info["read_me_response_path"]=read_me_response_path
            
            module_info = save_module_info(module_info)
        # Save to module_info
            print(f"Results saved to: {info_file_path}")
        
        for module_path in module_info.get('module_paths'):
            
            basename = os.path.basename(module_path)
            if basename in AVOID_LIST:
                script_data = AVOID_LIST.get(basename)
            else:
                script_data = read_from_file(module_path)
                
            module_info,partial_path = get_partial_path(module_info,module_path)
            partial_descriptions = get_partial_descriptions(module_info)
            meta_data = module_info.get('meta_data')
            if not module_info.get(partial_path):
                human_readable_data = generate_description_from_metadata(meta_data)
                prompt = f"""the data provided is {basename} from partial path {partial_path} in {human_readable_data}\n\n here is a synopsis of the previous scripts: {partial_descriptions}\n\nplease overview the script provided in the chunk_data and derive a description/summary of the script as it relates to the module; this will later be amalgamated with the various portions of the whole module descriptions to create a comprehensive readme\n"""
                response = make_api_call(prompt=prompt,
                                         completion_percentage=60,
                                         data=script_data)
                module_info[partial_path] = response
                update_json_data(module_info, partial_path)
                save_module_info(module_info)
        
        if not os.path.isfile(module_info["read_me_response_path"]):
            prompt = get_readme_prompt(meta_data=module_info["meta_data"],
                                   complete_synopsis=get_complete_synopsis(module_info),
                                   module_directory=module_info["meta_data"],
                                   imports=module_info["Imports"],
                                   module_paths=module_info["module_paths"])
            response = make_api_call(prompt=prompt,
                                     completion_percentage=80)
            safe_dump_to_file(data=response,file_path=module_info["read_me_response_path"])
        print(f"{module_directory} COMPLETE!!")

