from typing import Union, List, get_origin, get_args
from inspect import _empty


def not_needed(self):
    if self.type in (_empty, str, type(None)):
        return True


def to_int(self):
    try:
        self.input = int(self.input)
    except ValueError:
        try:
            self.input = int(float(self.input))
        except ValueError:
            return False
    return True


def to_float(self):
    try:
        self.input = float(self.input)
    except ValueError:
        return False
    return True


def resolve_basic_typehint(self, _type=None) -> bool:
    if _type is None:
        _type = self.type
    if not_needed(self):
        return True
    elif _type is int:
        to_int(self)
    elif _type is float:
        to_float(self)
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
    elif get_origin(arg) is List:
        if resolve_list(self, arg):
            return True
    else:
        return resolve_basic_typehint(self, arg)
    return False


def resolve_union(self, _type=None):
    args = get_args(self.type) if _type is None else get_args(_type)
    if not args:
        return False
    for arg in args:
        if get_origin(arg) is List and resolve_list(self, arg):
            return True
        resolved = resolve_basic_typehint(self, arg)
        if resolved:
            return True
    return False
