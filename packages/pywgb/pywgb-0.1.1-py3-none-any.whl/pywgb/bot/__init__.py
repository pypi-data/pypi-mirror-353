#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
All bot classes

- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 13:54
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

from .text import TextBot
from .markdown import MarkdownBot
from .image import ImageBot
from .news import NewsBot
from .file import FileBot
from .voice import VoiceBot
from .template_card.text import TextCardBot
from .template_card.news import NewsCardBot

__all__ = [
    "TextBot",
    "MarkdownBot",
    "ImageBot",
    "NewsBot",
    "FileBot",
    "VoiceBot",
    "TextCardBot",
    "NewsCardBot",
]
