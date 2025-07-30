from setuptools import setup, find_packages
import os

# README.md 파일 읽기
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="junLib",
    version="0.1.1",
    description="파이썬 유틸리티 라이브러리",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="jslee7518",
    author_email="jslee7518@gmail.com",
    url="https://github.com/jslee7518/junLib",
    packages=find_packages(),
    package_dir={"junLib": "library"},
    install_requires=[
        "PyQt5",
        "moviepy",
        "pandas",
        "tqdm",
        "watchdog",
        "distro",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
