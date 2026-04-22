import ast

def extract_signatures(file_path, methods):
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
    
    results = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in methods:
            args_list = []
            
            # Positional-only arguments
            if hasattr(node.args, 'posonlyargs') and node.args.posonlyargs:
                for arg in node.args.posonlyargs:
                    args_list.append(arg.arg)
                args_list.append('/')
            
            # Positional or keyword arguments
            for arg in node.args.args:
                args_list.append(arg.arg)
            
            # Variable positional arguments (*args)
            if node.args.vararg:
                args_list.append(f"*{node.args.vararg.arg}")
            elif node.args.kwonlyargs:
                if '/' not in args_list and '*' not in args_list:
                    # Logic is slightly complex for when to insert *, 
                    # but if there are kwonlyargs and no *args, we need *
                    pass
            
            # Keyword-only arguments
            if node.args.kwonlyargs:
                if not node.args.vararg:
                    args_list.append('*')
                for arg in node.args.kwonlyargs:
                    args_list.append(arg.arg)
            
            # Variable keyword arguments (**kwargs)
            if node.args.kwarg:
                args_list.append(f"**{node.args.kwarg.arg}")
                
            results[node.name] = f"def {node.name}({', '.join(args_list)})"
    
    for method in methods:
        if method in results:
            print(results[method])

methods = [
    "update_object", "update_property", "delete_property", "delete_object",
    "add_scenario", "list_parent_objects", "list_child_objects",
    "list_object_memberships", "iterate_properties", "validate_database",
    "backup_database", "to_csv", "list_models", "list_scenarios_by_model"
]
extract_signatures("src/plexosdb/db.py", methods)
