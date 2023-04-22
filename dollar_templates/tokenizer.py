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
    l = list(template)
    current = list()
    current_type = "plain"
    while len(l) > 0:
        if current_type == "plain":
            try:
                next_dollar = l.index('$')
            except ValueError:
                current.extend(l)
                l = []; break
            current.extend(l[:next_dollar])
            l = l[next_dollar:]
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
