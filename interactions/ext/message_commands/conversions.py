from typing import Union, List, get_origin, get_args
from inspect import _empty
from shlex import split


def not_needed(self):
    if self.type in (_empty, str, type(None)):
        return True


def to_int(self):
    if isinstance(self.input, list):
        for i in self.input:
            try:
                self.input[self.input.index(i)] = int(i)
            except ValueError:
                try:
                    self.input[self.input.index(i)] = int(float(i))
                except ValueError:
                    return False
    else:
        try:
            self.input = int(self.input)
        except ValueError:
            try:
                self.input = int(float(self.input))
            except ValueError:
                return False
    return True


def to_float(self):
    if isinstance(self.input, list):
        for i in self.input:
            try:
                self.input[self.input.index(i)] = float(i)
            except ValueError:
                return False
    else:
        try:
            self.input = float(self.input)
        except ValueError:
            return False
    return True


def resolve_basic_typehint(self, _type=None) -> bool:
    if _type is None:
        _type = self.type

    if _type is int:
        to_int(self)
    elif _type is float:
        to_float(self)
    elif not_needed(self):
        return True
    else:
        return False
    return True


def resolve_list(self, _arg=None):
    if _arg is None:
        args = get_args(self.type)
        if not args:
            return False
        arg = args[0]
    else:
        arg = _arg
    if get_origin(arg) is Union:
        if resolve_union(self, arg):
            return True
    elif get_origin(arg) == list:
        print("resolve", [resolve_list(self, a) for a in get_args(arg)])
        if any(resolve_list(self, a) for a in get_args(arg)):
            return True
    else:
        return resolve_basic_typehint(self, arg)
    return False


def resolve_union(self, _type=None):
    args = get_args(self.type) if _type is None else get_args(_type)
    if not args:
        return False
    self.input = split(self.input) if len(split(self.input)) > 1 else list(self.input)
    print("input", self.input)
    print("args", args)
    print(f"{get_origin(args[0]) == list}??")
    for arg in args:
        if get_origin(arg) == list and resolve_list(self, arg):
            print("yes")
            return True
        resolved = resolve_basic_typehint(self, arg)
        if resolved:
            return True
    return False
