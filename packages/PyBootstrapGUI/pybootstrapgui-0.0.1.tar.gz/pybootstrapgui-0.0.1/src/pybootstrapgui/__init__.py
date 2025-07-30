"""
my_module
=========

This package provides tools for data processing and analysis.

Modules:
- parser: functions to parse input files
- analyzer: statistical tools and computation
- exporter: utilities to export results

Example:
    from my_module import parser
    data = parser.load_file("data.csv")
"""

from . import base
from . import components
from . import extensions
from . import html_builder
from . import tag
from . import utils
from .bootstrap_builder import Page

__version__ = "0.0.1"
__bootstrap_version__ = "5.3.3"
__bootstrap_icons_version__ = "1.11.3"
