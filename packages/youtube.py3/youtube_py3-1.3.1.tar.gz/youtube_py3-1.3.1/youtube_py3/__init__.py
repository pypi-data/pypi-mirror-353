"""
YouTube.py3 - A simplified wrapper for YouTube Data API v3
"""

__version__ = "1.3.2"  # 1.2.0の次のバージョン
__author__ = "Chihalu"
__email__ = ""
__license__ = "MIT"

from .youtube_py3 import YouTubeAPI, YouTubeAPIError

__all__ = ["YouTubeAPI", "YouTubeAPIError"]
