
from setuptools import setup, find_packages
setup(
    name="IPython-Volr",
    version="0.1",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    description="An IPython extension to support executing Volr scripts",
    url="https://github.com/volr/ipython-volr"
)
