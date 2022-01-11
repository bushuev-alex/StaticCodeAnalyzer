import ast
import re

script = open("test_file.py").read()
tree = ast.parse(script)
nodes = ast.walk(tree)
for node in nodes:
    if isinstance(node, ast.FunctionDef):
        for default in node.args.defaults:
            none_dict = default.__dict__
            none = none_dict
            print(default)

"""        for default in node.args.defaults:
            b = default.__dict__
            try:
                print(b['value'])
            except KeyError:
                print(b['elts'])"""

