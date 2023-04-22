from setuptools import setup, find_packages

with open('readme.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dollar_templates',
    version='1.0.0',
    packages=['dollar_templates'],
    python_requires='>=3.9',
    author='Frank Seifferth',
    author_email='frankseifferth@posteo.net',
    description='Pandoc style dollar templates for python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/seifferth/dollar_templates',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License '
                                   'v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],
)
