# Pandoc style dollar templates for python

A slim reimplementation of pandoc's templating engine
in python. This allows you to use pandoc-style templates
(cf. <https://pandoc.org/MANUAL.html#template-syntax>) in any python
project, even if you do not want to use pandoc itself.

While this project aims to follow the template syntax described in
the pandoc documentation, it is a completely separate project and may
therefore behave differently than pandoc in certain situations. Especially
edge cases are not particularly well tested (yet). Also note that, as
of now, not all features found in pandoc's templating engine have been
implemented (see below). If you notice differences between pandoc and
`dollar_templates` concerning features that have been implemented,
feel free to submit a bug report or even a pull request.

## Usage

The easiest way to expand a template with some data is to use the
`apply_template` function:

```python
from dollar_templates import apply_template

template = "$for(var)$- $var$\n$endfor$"
metadata = {"var": [1,2,3]}

print(apply_template(template, metadata))
```

To parse the template once and apply it multiple times to different
data, use the `parse_template` function that returns an object of
type `dollar_templates.Template`.

```
from dollar_templates import parse_template

template = "$for(var)$- $var$\n$endfor$"
metadata_a = {"var": [1,2,3]}
metadata_b = {"var": [11,12,13]}

t = parse_template(template)
print(t.apply(metadata_a))
print(t.apply(metadata_b))
```

## Unit tests

Unit tests are implemented in `test_all.py` and can be executed with
[pytest](https://pytest.org). Simply install pytest and then execute
the `pytest` command in this directory without arguments.

## Implementation state

Pandoc lists the following features of its templating engine
(cf. <https://pandoc.org/MANUAL.html#template-syntax>):

- [x] Comments
- [x] Delimiters
- [x] Interpolated variables
- [x] Conditionals
- [x] For loops
- [ ] Partials
- [ ] Nesting
- [ ] Breakable spaces
- [ ] Pipes

The list above shows which ones have been implemented in dollar_templates.
The missing ones might or might not follow in the future.
