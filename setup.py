from setuptools import setup
setup(
    name = 'tappedtable',
    version = '0.2',
    description = 'A tool to take a tappedout.net url and convert the deck into an image for Tabletop Simulator',
    url = 'https://github.com/Berlox/tappedtable',
    author = 'Christian Dunn',
    py_modules = ['tappedtable'],
    install_requires=[
    'beautifulsoup4',
    'wxPython',
    'Pillow'
    ],
    license = 'MIT'
)
