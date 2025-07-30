"""
Setup script for YouTube.py3
"""

from setuptools import setup, find_packages
import os


def get_version():
    """バージョン情報を取得"""
    version_file = os.path.join(os.path.dirname(__file__), 'youtube_py3', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"').strip("'")
    return "1.0.0"


def get_long_description():
    """Get long description directly"""
    return """
# YouTube.py3

A simplified and intuitive Python wrapper for the YouTube Data API v3.

## Features

- Easy-to-use interface for YouTube Data API v3
- Comprehensive video, channel, and playlist operations
- Built-in error handling and rate limiting
- Support for OAuth2 authentication
- Lightweight and minimal dependencies
- Full type hints support

## Quick Start

```python
from youtube_py3 import YouTubeAPI

# Initialize with API key
youtube = YouTubeAPI(api_key="your_api_key_here")

# Get video information
video = youtube.get_video("video_id_here")
print(f"Title: {video.title}")
print(f"Views: {video.view_count}")

# Search for videos
results = youtube.search("Python programming", max_results=10)
for video in results:
    print(f"{video.title} - {video.channel_title}")
```

## Installation

```bash
pip install youtube.py3
```

## Requirements

- Python 3.7+
- Google API Python Client
- Valid YouTube Data API v3 key

## Documentation

For detailed documentation and examples, visit the [GitHub repository](https://github.com/Himarry/youtube.py3).

## License

This project is licensed under the MIT License.
"""


long_description = get_long_description()

setup(
    name="youtube.py3",
    version=get_version(),
    author="Chihalu",
    author_email="",
    description="A simplified wrapper for YouTube Data API v3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Himarry/youtube.py3",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "google-api-python-client>=2.0.0",
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=0.5.0",
        "google-auth-httplib2>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
            "twine>=4.0.0",
            "build>=0.8.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    keywords="youtube api wrapper python google data v3",
    project_urls={
        "Bug Reports": "https://github.com/Himarry/youtube.py3/issues",
        "Source": "https://github.com/Himarry/youtube.py3",
        "Documentation": "https://github.com/Himarry/youtube.py3#readme",
        "Homepage": "https://github.com/Himarry/youtube.py3",
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "youtube-py3=youtube_py3.cli:main",
        ],
    },
)
