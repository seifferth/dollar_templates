#!/usr/bin/env python3

from dollar_templates import apply_template

template_A = """
$if(one)$
One is set
$elseif(two)$
  $if(one)$
  Both one and two are set
  $else$
  Only two is set
  $endif$
$else$
Neither one nor two are set
$endif$
"""

template_B = """
This is some heading

$body$

This is some footer

$-- Comment
$for(forloop.content)$- $forloop.content$
$endfor$

And some if stuff

$if(doesnotexist)$doesnotexist does exist$else$if is $ifstate$$endif$

$if(one)$one$elseif(two)$two$elseif(three)$three$else$bigger than three$endif$
"""

def test_001():
    t = template_A
    m = {
        'body': 'text',
        'forloop': { 'content': ['one', 'two', 'three'] },
        'endmap': { 'first': 'hi', 'second': 'there' },
        'ifstate': 'not true',
        'three': 3,
    }
    assert apply_template(t, m).strip() == 'Neither one nor two are set'

def test_002():
    t = template_B
    m = {
        'body': 'text',
        'forloop': { 'content': ['one', 'two', 'three'] },
        'endmap': { 'first': 'hi', 'second': 'there' },
        'ifstate': 'not true',
        'three': 3,
    }
    assert apply_template(t, m).strip() == \
        'This is some heading\n\ntext\n\nThis is some footer\n\n' \
        '- one\n- two\n- three\n\n\nAnd some if stuff\n\nif is not true' \
        '\n\nthree'

def test_003():
    t = template_A
    m = {'one': 'true', 'two': 'true'}
    assert apply_template(t, m).strip() == 'One is set'

def test_004():
    t = template_A
    m = {'one': '', 'two': 'true'}
    assert apply_template(t, m).strip() == 'Only two is set'

template_mymap = """
$for(mymap)$
$it.last$, $it.first$
$endfor$
"""

def test_005():
    t = template_mymap
    m = {'mymap': {'first': 'John', 'last': 'Doe'}}
    assert apply_template(t, m).strip() == 'Doe, John'

def test_006():
    t = '$for(array)$$array$$sep$, $endfor$'
    m = {'array': [1,2,3,4]}
    assert apply_template(t, m) == '1, 2, 3, 4'
