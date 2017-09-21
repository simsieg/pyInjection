#!/usr/bin/env python

from __future__ import print_function

import ast
import sys
import fileinput
import json
version_info = (0, 1, 3)
__version__ = '.'.join(map(str, version_info))


def stringify(node):
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return '%s.%s' % (stringify(node.value), node.attr)
    elif isinstance(node, ast.Subscript):
        return '%s[%s]' % (stringify(node.value), stringify(node.slice))
    elif isinstance(node, ast.Index):
        return stringify(node.value)
    elif isinstance(node, ast.Call):
        return '%s(%s, %s)' % (stringify(node.func), stringify(node.args), stringify(node.keywords))
    elif isinstance(node, list):
        return '[%s]' % (', '.join(stringify(n) for n in node))
    elif isinstance(node, ast.Str):
        return node.s
    else:
        return ast.dump(node)


class IllegalLine(object):
    def __init__(self, reason, node, filename):
        self.reason = reason
        self.lineno = node.lineno
        self.filename = filename
        self.node = node

    def toDict(self):
        return {'file': self.filename, 'line': self.lineno, 'message': self.reason}

    def __str__(self):
        return "%s:%d\t%s" % (self.filename, self.lineno, self.reason)

    def __repr__(self):
        return "IllegalLine<%s, %s:%s>" % (self.reason, self.filename, self.lineno)


def find_assignment_in_context(variable, context):
    if isinstance(context, (ast.FunctionDef, ast.Module, ast.For, ast.While, ast.With, ast.If)):
        for node in reversed(list(ast.iter_child_nodes(context))):
            if isinstance(node, ast.Assign):
                if variable in (stringify(c) for c in node.targets):
                    return node
    if getattr(context, 'parent', None):
        return find_assignment_in_context(variable, context.parent)
    else:
        return None


class Checker(ast.NodeVisitor):
    def __init__(self, filename, *args, **kwargs):
        self.filename = filename
        self.errors = []
        super(Checker, self).__init__(*args, **kwargs)

    def check_execute(self, node):
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Mod):
                return IllegalLine('String interpolation of SQL query', node, self.filename)
            elif isinstance(node.op, ast.Add):
                return IllegalLine('String concatenation of SQL query', node, self.filename)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == 'format':
                    return IllegalLine('str.format called on SQL query', node, self.filename)
        elif isinstance(node, ast.Name):
            assignment = find_assignment_in_context(node.id, node)
            if assignment is not None:
                return self.check_execute(assignment.value)

    def visit_Call(self, node):
        function_name = stringify(node.func)
        if function_name.lower().endswith('.execute'):
            try:
                node.args[0].parent = node
                node_error = self.check_execute(node.args[0])
                if node_error:
                    self.errors.append(node_error)
            except IndexError:
                pass
        elif function_name.lower() == 'eval':
            self.errors.append(IllegalLine('eval() is generally dangerous', node, self.filename))
        self.generic_visit(node)

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        item.parent = node
                        self.visit(item,)
            elif isinstance(value, ast.AST):
                value.parent = node
                self.visit(value)


def check(filename, args):
    c = Checker(filename=filename)
    if filename == '-':
        fobj = sys.stdin
    else:
        fobj = open(filename, 'r')

    try:
        parsed = ast.parse(fobj.read(), filename)
        c.visit(parsed)
    except Exception:
        raise
    return c.errors


def create_parser():
    import argparse
    parser = argparse.ArgumentParser(
        description='Look for patterns in python source files that might indicate SQL injection or other vulnerabilities',
        epilog='Exit status is 0 if all files are okay, 1 if any files have an error. Found vulnerabilities are printed to standard out'
    )
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('files', nargs='*', help='files to check or \'-\' for standard in')
    parser.add_argument('-j', '--json', action='store_true', help='print output in JSON')
    parser.add_argument('-s', '--stdin', action='store_true', help='read from standard in, passed files are ignored')
    parser.add_argument('-q', '--quiet', action='store_true', help='do not print error statistics')

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not (args.files or args.stdin):
        parser.error('incorrect number of arguments')
    if args.stdin:
        args.files = ['-']

    errors = []
    for fname in args.files:
        errors.extend(check(fname, args))
    if errors:
        if args.json:
            print(json.dumps(map(lambda x: x.toDict(), errors),
                indent=2, sort_keys=True))
        else:
            print('\n'.join(str(e) for e in errors))
        if not args.quiet:
            print('Total errors: %d' % len(errors), file=sys.stderr)
        return 1
    else:
        return 0


if __name__ == '__main__':
    sys.exit(main())
