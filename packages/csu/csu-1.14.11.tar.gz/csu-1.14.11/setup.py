#!/usr/bin/env python
import re
from pathlib import Path

from setuptools import find_namespace_packages
from setuptools import setup


def read(*names, **kwargs):
    with Path(__file__).parent.joinpath(*names).open(encoding=kwargs.get("encoding", "utf8")) as fh:
        return fh.read()


setup(
    name="csu",
    version="1.14.11",
    license="BSD-2-Clause",
    description="Clean Slate Utils - bunch of utility code, mostly Django/DRF specific.",
    long_description="{}\n{}".format(
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub("", read("README.rst")),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    long_description_content_type="text/x-rst",
    author="Ionel Cristian Mărieș",
    author_email="contact@ionelmc.ro",
    url="https://github.com/ionelmc/python-csu",
    packages=find_namespace_packages("src"),
    package_dir={"": "src"},
    py_modules=[path.stem for path in Path("src").glob("*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        # uncomment if you test on these interpreters:
        # "Programming Language :: Python :: Implementation :: IronPython",
        # "Programming Language :: Python :: Implementation :: Jython",
        # "Programming Language :: Python :: Implementation :: Stackless",
        "Topic :: Utilities",
    ],
    project_urls={
        "Changelog": "https://github.com/ionelmc/python-csu/blob/master/CHANGELOG.rst",
        "Issue Tracker": "https://github.com/ionelmc/python-csu/issues",
    },
    keywords=[
        # eg: "keyword1", "keyword2", "keyword3",
    ],
    python_requires=">=3.10",
    install_requires=[
        "django",
        "djangorestframework",
        "django-crispy-forms",
        "django-import-export",
        "httpx",
        "typing-extensions",
        "defusedxml",
    ],
    extras_require={
        "phonenumber": [
            "phonenumberslite",
            "django-phonenumber-field",
        ],
    },
)
