import re
import os
import argparse
import ast

parser = argparse.ArgumentParser()
parser.add_argument("path", default='.')
args = parser.parse_args()
params = [args.path]


class Checker:
    def __init__(self, data):
        self.path = data[0]
        self.codes = {'S001': 'Too long',
                      'S002': 'Indentation is not a multiple of four',
                      'S003': 'Unnecessary semicolon after a statement',
                      'S004': 'Less than two spaces before inline comments',
                      'S005': 'TODO found',
                      'S006': 'More than two blank lines preceding a code line',
                      'S007': "Too many spaces after '{}'",
                      'S008': "Class name '{}' should be written in CamelCase",
                      'S009': 'Function name {} should be written in snake_case',
                      'S010': "Argument name {} should be written in snake_case",
                      'S011': "Variable {} should be written in snake_case",
                      'S012': "Default argument value is mutable"}
        self.errors = []
        self.blank_line_count = 0

    def blank_line(self, m_line):
        if m_line.strip() != '':
            self.blank_line_count = 0

    def error_s001(self, m, m_line):  # 'Too long'
        if len(m_line) > 79:
            self.errors.append([m, f"{self.path}: Line {m}: S001 {self.codes['S001']}"])

    def error_s002(self, m, m_line):  # Indentation is not a multiple of four
        if len(re.match('^ *', m_line)[0]) % 4 != 0:
            self.errors.append([m, f"{self.path}: Line {m}: S002 {self.codes['S002']}"])

    def error_s003(self, m, m_line):  # Unnecessary semicolon after a statement
        if ";" in m_line:
            if re.match(".*#.*;.*", m_line):
                return True
            elif re.match(""".*('|").*;.*('|").*""", m_line) is None:
                self.errors.append([m, f"{self.path}: Line {m}: S003 {self.codes['S003']}"])

    def error_s004(self, m, m_line):  # Less than two spaces before inline comments
        if '#' in m_line:
            if re.match("^#.*", m_line):
                pass
            elif re.match('.*( ){2,}#.*', m_line) is None and '#' in m_line:
                self.errors.append([m, f"{self.path}: Line {m}: S004 {self.codes['S004']}"])

    def error_s005(self, m, m_line):  # TO_DO found (in comments only and case-insensitive)
        if re.match('.*#.*TODO.*', m_line, re.IGNORECASE):
            self.errors.append([m, f"{self.path}: Line {m}: S005 {self.codes['S005']}"])

    def error_s006(self, m, m_line):  # More than two blank lines preceding a code line
        if m_line.strip() == '':
            self.blank_line_count += 1
            if self.blank_line_count > 2:
                self.errors.append([m+1, f"{self.path}: Line {m+1}: S006 {self.codes['S006']}"])
                self.blank_line_count = 0

    def error_s007(self, m, m_line):  # Too many spaces after construction_name (def or class)
        if re.match(".*(class|def) {2,}.*", m_line):
            beginning_line = re.match(".*(class|def) {2,}", m_line)[0]
            if 'class' in beginning_line:
                name = m_line[len(beginning_line):-2]
            elif 'def' in beginning_line:
                name = m_line[len(beginning_line):-4]
            self.errors.append([m, f"{self.path}: Line {m}: S007 {self.codes['S007'].format(name)}"])

    def error_s008(self, m, m_line):  # Class name {} should be written in CamelCase
        if 'class' in m_line:
            if not re.match(".* ?class [A-Z][a-zA-Z]*(\\([A-Z][a-zA-Z]*\\))?:", m_line):
                if re.match(".*class [a-z]+", m_line):
                    beginning_line = re.match(".*class +[A-Z]?", m_line)[0]
                    class_name = m_line[len(beginning_line):-2]
                    self.errors.append([m, f"{self.path}: Line {m}: S008 {self.codes['S008'].format(class_name)}"])

    def error_s009(self, m, m_line):  # Function name {} should be written in snake_case
        if 'def' in m_line:
            if not re.match(".*def _{,2}?[a-z]*_?[a-z0-9]*_{,2}?\\(.*\\):$", m_line):
                if re.match(".*def +[A-Z]", m_line):
                    beginning_line = re.match(".*def +[a-z]?", m_line)[0]
                    def_name = m_line[len(beginning_line):-4]
                    self.errors.append([m, f"{self.path}: Line {m}: S009 {self.codes['S009'].format(def_name)}"])

    def check_file(self):
        if re.match('.*\\.py$', self.path):
            with open(self.path, 'r', encoding="UTF-8") as file:
                n = 1
                for line in file:
                    self.blank_line(line)
                    self.error_s001(n, line)  # Too long
                    self.error_s002(n, line)  # Indentation is not a multiple of four
                    self.error_s003(n, line)  # Unnecessary semicolon after a statement
                    self.error_s004(n, line)  # Less than two spaces before inline comments
                    self.error_s005(n, line)  # TO_DO found (in comments only and case-insensitive)
                    self.error_s006(n, line)  # More than two blank lines preceding a code line
                    self.error_s007(n, line)  # Too many spaces after construction_name (def or class)
                    self.error_s008(n, line)  # Class name {} should be written in CamelCase
                    self.error_s009(n, line)  # Function name {} should be written in snake_case
                    n += 1

            # AST checkers
            with open(self.path, 'r', encoding="UTF-8") as file:
                text = file.read()
                tree = ast.parse(text)
                nodes = ast.walk(tree)
                for node in nodes:
                    if isinstance(node, ast.FunctionDef):
                        for obj in node.args.args:  # Argument name {} should be written in snake_case
                            func = obj.__dict__
                            lineno = func['lineno']
                            arg_name = func['arg']
                            if not re.match("^[a-z0-9_]*_?[a-z0-9]*$", arg_name):
                                self.errors.append([lineno, f"{self.path.lower()}: Line {lineno}: S010 {self.codes['S010'].format(arg_name)}"])  #
                        for obj in node.body:  # Variable {} should be written in snake_case
                            if isinstance(obj, ast.Assign):
                                for target in obj.targets:
                                    var_dict = target.__dict__
                                    try:
                                        var_name = var_dict['id']
                                        lineno = var_dict['lineno']
                                    except KeyError:
                                        var_name = var_dict['value'].id + '.' + var_dict['attr']
                                        lineno = var_dict['lineno']
                                    if not re.match("^[a-z0-9_]*\.?_?[a-z0-9]*$", var_name):
                                        self.errors.append([lineno, f"{self.path}: Line {lineno}: S011 {self.codes['S011'].format(var_name)}"])
                        for default in node.args.defaults:  # The default argument value is mutable
                            if isinstance(default, ast.List) or isinstance(default, ast.Dict) \
                                    or isinstance(default, ast.Set):
                                default_dict = default.__dict__
                                lineno = default_dict['lineno']
                                self.errors.append([lineno, f"{self.path}: Line {lineno}: S012 {self.codes['S012']}"])

    def check_dir(self):
        file_list = os.listdir(self.path)
        for file in file_list:
            path = self.path
            self.path = self.path + f'{os.sep}' + file
            self.check_file()
            self.path = path

    def dir_or_file(self):
        if os.path.isdir(self.path):
            return "dir"
        elif os.path.isfile(self.path):
            return "file"

    def print_errors(self):
        self.errors.sort()
        for error in self.errors:
            print(error[1].strip().lower())


my_checker = Checker(params)

if my_checker.dir_or_file() == 'file':
    my_checker.check_file()
elif my_checker.dir_or_file() == 'dir':
    my_checker.check_dir()
my_checker.print_errors()
