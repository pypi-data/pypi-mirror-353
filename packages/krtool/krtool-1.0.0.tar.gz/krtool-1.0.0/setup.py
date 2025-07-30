import codecs
import os
from setuptools import setup, find_packages

# these things are needed for the README.md show on pypi (if you dont need delete it)
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# you need to change all these
VERSION = '1.0.0'
DESCRIPTION = 'Perform simple operations on the MySQL database without entering SQL commands.'
LONG_DESCRIPTION = 'The functionality is very simple; if you are proficient in using MySQL, then this project is unnecessary.'

setup(
    name="krtool",
    version=VERSION,
    author="Xuchang Su",
    author_email="krlrtear@163.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pymysql'],
    keywords=['python', 'windows', 'mysql'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
