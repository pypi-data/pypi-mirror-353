from setuptools import setup
import tomli

# pyproject.toml 파일 읽기
with open("pyproject.toml", "rb") as f:
    pyproject = tomli.load(f)

# README.md 파일 읽기
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# pyproject.toml에서 프로젝트 정보 가져오기
project = pyproject["project"]

setup(
    name=project["name"],
    version=project["version"],
    description=project["description"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=project["authors"][0]["name"],
    author_email=project["authors"][0]["email"],
    python_requires=project["requires-python"],
    install_requires=project["dependencies"],
    packages=["library"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
