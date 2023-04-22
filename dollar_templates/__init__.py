#!/usr/bin/env python3

from .tokenizer import tokenize
from .parser import parse_tokens
from .syntax import Tree as _Tree

class Template():
    def __init__(self, template: str):
        self.tree: _Tree = parse_tokens(tokenize(template))
    def apply(self, metadata: dict) -> str:
        return self.tree.apply(metadata)
    def __repr__(self) -> str:
        return f'Template:{self.tree}'
def parse_template(template: str) -> Template:
    return Template(template)
def apply_template(template: str, metadata: dict) -> str:
    return parse_template(template).apply(metadata)
