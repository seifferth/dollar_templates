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
    def split_list(l: list, char: str) -> tuple[list,list]:
        """
        Returns two lists. The first list is the one containing everything
        up to (but excluding) char, the second one is possibly empty;
        but if it is not empty, it holds char at index 0 as well as
        whatever follows char in the original list.
        """
        try:
            next = l.index(char)
            part = l[:next]; l = l[next:]
        except ValueError:
            part = l; l = []
        return part, l
    l = list(template)
    current = list()
    current_type = "plain"
    while len(l) > 0:
        if current_type == "plain":
            head, l = split_list(l, '$')
            current.extend(head)
            if len(l) == 0: break
            if l[:2] == ['$','$']:          # Literal $
                current.append("$"); l.pop(0); l.pop(0)
            elif l[:3] == ['$','-','-']:    # Line comment
                head, l = split_list(l, '\n')
                l.pop(0)
            elif l[:2] == ['$', '{']:
                l.pop(0); l.pop(0)
                yield PlainToken("".join(current))
                current = list()
                head, l = split_list(l, '}')
                yield MetaToken("".join(head))
                l.pop(0)
                current_type = "plain"
            elif l[:1] == ['$']:
                l.pop(0)
                yield PlainToken("".join(current))
                current = list()
                head, l = split_list(l, '$')
                yield MetaToken("".join(head))
                l.pop(0)
                current_type = "plain"
            else:
                raise Exception('Internal Error: This branch should never '
                                'be executed. There is probably something '
                                'wrong with the optimization for long plain '
                                'contents at the beginning of this loop.')
    yield PlainToken("".join(current)) if current_type == "plain" else \
          MetaToken("".join(current))
