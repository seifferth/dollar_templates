#!/usr/bin/env python3

import sys
import re
from typing import Union
from copy import deepcopy

class Token():
    def __init__(self, content: str):
        self.content = content
    def __repr__(self):
        content = self.content \
            .replace('\\', '\\\\') \
            .replace('"', '\"') \
            .replace('\t', '\\t') \
            .replace('\n', '\\n')
        return f'{type(self).__name__}<{content}>'
class PlainToken(Token):
    pass
class MetaToken(Token):
    pass

def __tokenize(template: str) -> list[Union[PlainToken, MetaToken]]:
    l = list(template)
    current = list()
    current_type = "plain"
    while len(l) > 0:
        if current_type == "plain":
            if l[:2] == ['$','$']:          # Literal $
                current.append("$"); l.pop(0); l.pop(0)
            elif l[:3] == ['$','-','-']:    # Line comment
                while l[0] != '\n':
                    l.pop(0)
                l.pop(0)
            elif l[0] != '$':
                current.append(l.pop(0))
            elif l[0] == '$' and l[1] == '{':
                l.pop(0); l.pop(0)
                yield PlainToken("".join(current))
                current = list()
                current_type = "meta_curly"
            else:   # l[0] == "$"
                l.pop(0)
                yield PlainToken("".join(current))
                current = list()
                current_type = "meta"
        elif current_type == "meta":
            if l[0] != "$":
                current.append(l.pop(0))
            else:   # l[0] == "$"
                l.pop(0)
                yield MetaToken("".join(current).strip())
                current = list()
                current_type = "plain"
        elif current_type == "meta_curly":
            if l[0] != "}":
                current.append(l.pop(0))
            else:   # l[0] == "}"
                l.pop(0)
                yield MetaToken("".join(current).strip())
                current = list()
                current_type = "plain"
    yield PlainToken("".join(current)) if current_type == "plain" else \
          MetaToken("".join(current))

def getvar(metadata: dict, varname: str) -> Union[str,list,dict]:
    d = metadata
    for key in varname.split('.'):
        if type(d) != dict: return ''
        d = d.get(key, '')
    if type(d) not in (list,dict): d = str(d)
    return d
def setvar(metadata: dict, newvars: dict) -> dict:
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
    def __init__(self, token: PlainToken):
        self.content = token.content
    def apply(self, metadata: dict) -> str:
        return self.content
class Var(TreeElement):
    def __init__(self, token: MetaToken):
        self.name = token.content
    def apply(self, metadata: dict) -> str:
        val = getvar(metadata, self.name)
        if type(val) == list:   return ''.join(val)
        elif type(val) == dict: return 'true'
        else:                   return val
class If(TreeElement):
    def __init__(self, condition: str, thenarm: TreeElement, elsearm: TreeElement):
        self.condition = condition
        self.thenarm = thenarm
        self.elsearm = elsearm
    def apply(self, metadata: dict) -> None:
        if getvar(metadata, self.condition) == '':
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
        data = getvar(metadata, self.it)
        if type(data) != list:
            res.append(self.main.apply(setvar(metadata, {'it': data})))
        else:   # type(data) == list
            for i, it in enumerate(data):
                res.append(self.main.apply(setvar(
                    metadata, {'it': it, self.it: it}
                )))
                if self.sep != None and i < len(data)-1:
                    res.append(self.sep.apply(setvar(
                            metadata, {'it': it, self.it: it}
                    )))
        return "".join(res)
class Tree(TreeElement):
    def __init__(self, tokens: list[TreeElement]):
        self.tokens = tokens
    def apply(self, metadata: dict) -> str:
        return "".join([x.apply(metadata) for x in self.tokens])

# Note: Parse functions consume (part of) the tokens they receive as
#       their argument.

def __parse_if(tokens: list[Token]) -> If:
    l = tokens
    assert l[0].content[:3] == 'if(' and l[0].content[-1:] == ')'
    condition = l.pop(0).content[3:-1]
    thentree, end = __parse(l, endtokens=[r'elseif\(.*\)', 'else', 'endif'])
    if end == 'else':
        elsetree, end = __parse(l, endtokens=['endif'])
    elif end.startswith('elseif('):
        assert end[:4] == 'else'
        l.insert(0, MetaToken(end[4:]))
        elsetree, _ = __parse(l, endtokens=['endif'])
    else:
        elsetree = PlainLeaf(PlainToken(''))
    return If(condition, thentree, elsetree)
def __parse_for(tokens: list[Token]) -> For:
    l = tokens
    assert l[0].content[:4] == "for(" and l[0].content[-1:] == ")"
    it = l.pop(0).content[4:-1]
    main, end = __parse(l, endtokens=['sep', 'endfor'])
    sep = __parse(l, endtokens=['endfor'])[0] if end == 'sep' else None
    return For(it, main, sep)

def __parse(tokens: list[Token], endtokens: list[str]=None) -> tuple[Tree,str]:
    """Returns a tuple (tree, matching_endtoken)"""
    l = tokens
    res = list()
    while len(l) > 0:
        if type(l[0]) == PlainToken:
            res.append(Str(l.pop(0)))
        elif type(l[0]) == MetaToken:
            if endtokens != None:
                for t in endtokens:
                    if re.fullmatch(t, l[0].content):
                        return (Tree(res), l.pop(0).content)
            if re.fullmatch(r'if\(.*\)', l[0].content):
                res.append(__parse_if(l))
            elif re.fullmatch(r'for\(.*\)', l[0].content):
                res.append(__parse_for(l))
            else:
                res.append(Var(l.pop(0)))
    return (Tree(res), None)

class Template():
    def __init__(self, tree: Tree):
        self.tree = tree
    def apply(self, metadata: dict) -> str:
        return self.tree.apply(metadata)
    def __repr__(self) -> str:
        return f'Template:{self.tree}'
def parse_template(template: str) -> Template:
        tokens = list(filter(
            lambda x: not (type(x) == PlainToken and x.content == ""),
            __tokenize(template)
        ))
        tree, _ = __parse(tokens)
        return Template(tree)

def apply_template(template: str, metadata: dict) -> str:
    return parse_template(template).apply(metadata)
