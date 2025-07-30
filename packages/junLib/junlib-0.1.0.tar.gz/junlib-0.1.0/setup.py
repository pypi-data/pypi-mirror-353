from setuptools import setup, find_packages

setup(
    name="junLib",
    version="25.06.05.01",
    description="파이썬 유틸리티 라이브러리",
    author="spaceAnt",
    packages=find_packages(where="library"),
    package_dir={"": "library"},
    install_requires=[],
    python_requires=">=3.8",
)
