#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wecom(A.K.A. WeChat Work) Group Bot python API.


- Author: Rex Zhou <879582094@qq.com>
- Created Time: 2025/5/27 13:42
- Copyright: Copyright © 2025 Rex Zhou. All rights reserved.
"""

__author__ = 'Rex Zhou'
__copyright__ = 'Copyright © 2025 Rex Zhou. All rights reserved.'
__credits__ = [__author__]
__license__ = "MIT"
__maintainer__ = __author__
__email__ = '879582094@qq.com'

from .bot import TextBot
from .bot import MarkdownBot
from .bot import ImageBot
from .bot import NewsBot
from .bot import FileBot
from .bot import VoiceBot
from .bot import TextCardBot
from .bot import NewsCardBot
from .bot import SmartBot

__all__ = [
    "TextBot", "MarkdownBot", "ImageBot", "NewsBot", "FileBot", "VoiceBot",
    "TextCardBot", "NewsCardBot", "SmartBot"
]
