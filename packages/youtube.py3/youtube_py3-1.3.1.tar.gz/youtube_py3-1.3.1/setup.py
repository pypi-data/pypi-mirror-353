"""
Setup script for YouTube.py3 with enhanced Cython compilation
"""

from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import os
import re
from pathlib import Path

# numpyのインポートを条件付きに
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


def get_version():
    """バージョン情報を取得"""
    version_file = os.path.join(os.path.dirname(__file__), 'youtube_py3', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()
            version_match = re.search(r'^__version__\s*=\s*\'"[\'"]', content, re.MULTILINE)
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


def get_cython_extensions():
    """Cython拡張モジュールを取得（改良版）"""
    extensions = []
    
    # コンパイラディレクティブの設定
    compiler_directives = {
        'language_level': 3,
        'embedsignature': True,
        'boundscheck': False,
        'wraparound': False,
        'cdivision': True,
        'nonecheck': False,
        'overflowcheck': False,
        'initializedcheck': False,
        'infer_types': True,
        'binding': True,
    }
    
    # youtube_py3パッケージ内のPythonファイルを検索
    package_dir = Path("youtube_py3")
    if package_dir.exists():
        for py_file in package_dir.rglob("*.py"):
            # __init__.pyや特定のファイルは除外
            if py_file.name.startswith('__') or py_file.name in ['setup.py', 'test_']:
                continue
            
            # 相対パスからモジュール名を生成
            relative_path = py_file.relative_to(Path('.'))
            module_name = str(relative_path).replace(os.sep, '.').replace('.py', '')
            
            # インクルードディレクトリの設定
            include_dirs = []
            if NUMPY_AVAILABLE:
                include_dirs.append(np.get_include())
            
            # Extensionオブジェクトを作成
            ext = Extension(
                module_name,
                [str(py_file)],
                include_dirs=include_dirs,
                libraries=[],
                library_dirs=[],
                define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')] if NUMPY_AVAILABLE else [],
                extra_compile_args=['/O2'] if os.name == 'nt' else ['-O3', '-march=native'],
                extra_link_args=[],
            )
            extensions.append(ext)
    
    return extensions, compiler_directives


def create_cython_files():
    """PythonファイルをCythonファイル(.pyx)に変換"""
    package_dir = Path("youtube_py3")
    if not package_dir.exists():
        return
    
    for py_file in package_dir.rglob("*.py"):
        if py_file.name.startswith('__'):
            continue
        
        pyx_file = py_file.with_suffix('.pyx')
        if not pyx_file.exists() or py_file.stat().st_mtime > pyx_file.stat().st_mtime:
            print(f"Converting {py_file} to {pyx_file}")
            pyx_file.write_text(py_file.read_text(encoding='utf-8'), encoding='utf-8')


def main():
    """メイン処理"""
    # Cythonファイルを作成
    create_cython_files()
    
    # Cython拡張の設定
    extensions, compiler_directives = get_cython_extensions()
    ext_modules = []
    
    if extensions:
        print(f"Cythonizing {len(extensions)} modules...")
        
        # cythonizeのオプション
        cythonize_options = {
            'compiler_directives': compiler_directives,
            'build_dir': "build",
            'quiet': False,
            'annotate': True,  # HTMLレポートを生成
        }
        
        # 利用可能なCPUコア数を取得して並列化
        try:
            import multiprocessing
            nthreads = multiprocessing.cpu_count()
            cythonize_options['nthreads'] = nthreads
            print(f"Using {nthreads} threads for compilation")
        except:
            pass
        
        ext_modules = cythonize(extensions, **cythonize_options)
    
    # ビルド要件からnumpyを削除（オプション化）
    setup_requires = ["cython>=0.29.0"]
    if NUMPY_AVAILABLE:
        setup_requires.append("numpy>=1.19.0")
    
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
        setup_requires=setup_requires,
        keywords="youtube api wrapper python google data v3",
        project_urls={
            "Bug Reports": "https://github.com/Himarry/youtube.py3/issues",
            "Source": "https://github.com/Himarry/youtube.py3",
            "Documentation": "https://github.com/Himarry/youtube.py3#readme",
            "Homepage": "https://github.com/Himarry/youtube.py3",
        },
        include_package_data=True,
        zip_safe=False,
        # Cythonコンパイル時の最適化設定
        options={
            'build_ext': {
                'inplace': False,
                'force': True,
            }
        },
    )


if __name__ == "__main__":
    main()
