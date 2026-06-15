import argparse
import json
import sys

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PageData:
    url: str
    title: str
    links: list[str] = field(default_factory=list)
    text: str = ""


@dataclass
class PageData:
    url: str
    title: str
    links: list[str] = field(default_factory=list)
    text: str = ""@dataclass
class PageData:
    url: str
    title: str
    links: list[str] = field(default_factory=list)
    text: str = ""
