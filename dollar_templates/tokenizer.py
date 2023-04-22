#!/usr/bin/env python3

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

def tokenize(template: str) -> list[Token]:
    """
    Parse a template into a list of tokens. Tokens in the resulting list
    are either of type PlainToken or of type MetaToken. PlainToken is used
    for literal content. MetaToken is used for tokens that have a special
    meaning according to the template syntax, such as $var$, $if(var)$,
    $for(var)$, $endfor$ or $endif$.
    """
    def split_at(string: str, sep: str) -> tuple[str,str]:
        if sep not in string:
            return string, ""
        return string.split(sep, 1)
    current = list()
    rest = template
    while len(rest) > 0:
        head, rest = split_at(rest, '$')
        current.append(head)
        if rest[:1] == '$':             # Literal $
            current.append("$");
            rest = rest[1:]
        elif rest[:2] == '--':          # Line comment
            _head, rest = split_at(rest, '\n')
        elif rest[:1] == '{':
            yield PlainToken("".join(current)); current = list()
            head, rest = split_at(rest[1:], '}')
            yield MetaToken(head)
        else:                           # Dollar-enclosed MetaToken
            yield PlainToken("".join(current)); current = list()
            head, rest = split_at(rest, '$')
            yield MetaToken(head)
    if current: yield PlainToken("".join(current))
