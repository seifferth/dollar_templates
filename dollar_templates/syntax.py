#!/usr/bin/env python3

from typing import Union as _Union
from copy import deepcopy

def _getvar(metadata: dict, varname: str) -> _Union[str,list,dict]:
    d = metadata
    for key in varname.split('.'):
        try:
            d = d.__getitem__(key)
        except:
            return ''
    return d
def _setvar(metadata: dict, newvars: dict) -> dict:
    newdict = deepcopy(metadata)
    for varname, val in newvars.items():
        d = newdict
        for key in varname.split('.')[:-1]:
            if type(d.get(key, '')) != dict:
                d[key] = dict()
            d = d[key]
        d[varname.split('.')[-1]] = val
    return newdict

class TreeElement():
    def __repr__(self) -> str:
        res = list()
        res.append(f'{type(self).__name__}<')
        res.extend(['    ' + l for l in repr(self.__dict__).splitlines()])
        res.append('>')
        return '\n'.join(res)
class Str(TreeElement):
    def __init__(self, content: str):
        self.content = content
    def apply(self, metadata: dict) -> str:
        return self.content
class Var(TreeElement):
    def __init__(self, name: str):
        self.name = name
    def apply(self, metadata: dict) -> str:
        val = _getvar(metadata, self.name)
        if type(val) == list:   return ''.join(map(str, val))
        elif type(val) == dict: return 'true'
        else:                   return str(val)
class If(TreeElement):
    def __init__(self, condition: str, thenarm: TreeElement, elsearm: TreeElement):
        self.condition = condition
        self.thenarm = thenarm
        self.elsearm = elsearm
    def apply(self, metadata: dict) -> None:
        if _getvar(metadata, self.condition) == '':
            return self.elsearm.apply(metadata)
        else:
            return self.thenarm.apply(metadata)
class For(TreeElement):
    def __init__(self, it: str, main: TreeElement, sep: TreeElement):
        self.it = it
        self.main = main
        self.sep = sep
    def apply(self, metadata: dict) -> str:
        res = list()
        data = _getvar(metadata, self.it)
        if type(data) != list:
            res.append(self.main.apply(_setvar(metadata, {'it': data})))
        else:   # type(data) == list
            for i, it in enumerate(data):
                res.append(self.main.apply(_setvar(
                    metadata, {'it': it, self.it: it}
                )))
                if self.sep != None and i < len(data)-1:
                    res.append(self.sep.apply(_setvar(
                            metadata, {'it': it, self.it: it}
                    )))
        return "".join(res)
class Tree(TreeElement):
    def __init__(self, tokens: list[TreeElement]):
        self.tokens = tokens
    def apply(self, metadata: dict) -> str:
        return "".join([x.apply(metadata) for x in self.tokens])
