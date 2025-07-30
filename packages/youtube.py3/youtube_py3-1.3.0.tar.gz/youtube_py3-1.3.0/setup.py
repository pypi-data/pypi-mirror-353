"""
Setup script for YouTube.py3
"""

from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import os
import re


def get_version():
    """バージョン情報を取得"""
    version_file = os.path.join(os.path.dirname(__file__), 'youtube_py3', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 正規表現でバージョンを抽出
            version_match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE)
            if version_match:
                return version_match.group(1)
    return "1.3.0"


def get_long_description():
    """README.mdから長い説明を取得"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    return "A simplified wrapper for YouTube Data API v3"


def get_extensions():
    """Cython拡張モジュールを取得"""
    extensions = []
    
    # youtube_py3パッケージ内のPythonファイルを検索
    package_dir = "youtube_py3"
    if os.path.exists(package_dir):
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    # .pyファイルのパスを取得
                    py_file = os.path.join(root, file)
                    # モジュール名を生成
                    module_name = py_file.replace(os.sep, '.').replace('.py', '')
                    
                    # Extensionオブジェクトを作成（language_levelは削除）
                    extensions.append(Extension(
                        module_name,
                        [py_file]
                    ))
    
    return extensions


# Cython拡張の設定
extensions = get_extensions()
ext_modules = []
if extensions:
    ext_modules = cythonize(
        extensions,
        compiler_directives={
            'language_level': 3,
            'embedsignature': True,
            'boundscheck': False,
            'wraparound': False
        }
    )

setup(
    name="youtube.py3",
    version=get_version(),
    author="Chihalu",
    description="A simplified wrapper for YouTube Data API v3",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Himarry/youtube.py3",
    packages=find_packages(exclude=["tests", "tests.*"]),
    ext_modules=ext_modules,
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
    keywords="youtube api wrapper python google data v3",
    project_urls={
        "Bug Reports": "https://github.com/Himarry/youtube.py3/issues",
        "Source": "https://github.com/Himarry/youtube.py3",
        "Documentation": "https://github.com/Himarry/youtube.py3#readme",
        "Homepage": "https://github.com/Himarry/youtube.py3",
    },
    include_package_data=True,
    zip_safe=False,
)
