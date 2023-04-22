#!/usr/bin/env python3

import re
from .tokenizer import *
from .syntax import *

# Note: Internal __parse* functions consume (part of) the tokens they
# receive as their argument.
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
        elsetree = Str('')
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
            res.append(Str(l.pop(0).content))
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
                res.append(Var(l.pop(0).content))
    return (Tree(res), None)
def parse_tokens(tokens: list[Token]) -> Tree:
    """
    Parse a list of Tokens into an actual syntax Tree.
    """
    tokens = list(filter(
        lambda x: not (type(x) == PlainToken and x.content == ""),
        tokens
    ))
    tree, _ = __parse(tokens)
    return tree
