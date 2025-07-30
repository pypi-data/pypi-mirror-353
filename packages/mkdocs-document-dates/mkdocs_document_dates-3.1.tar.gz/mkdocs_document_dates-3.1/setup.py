from setuptools import setup, find_packages
import mkdocs_document_dates

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "An easy-to-use, lightweight MkDocs plugin for displaying the exact creation time, last modification time and author info of markdown documents."

VERSION = '3.1'

setup(
    name="mkdocs-document-dates",
    version=VERSION,
    author="Aaron Wang",
    description="An easy-to-use, lightweight MkDocs plugin for displaying the exact creation time, last modification time and author info of markdown documents.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaywhj/mkdocs-document-dates",
    packages=find_packages(),
    install_requires=[
        'mkdocs>=1.0.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'mkdocs.plugins': [
            'document-dates = mkdocs_document_dates.plugin:DocumentDatesPlugin',
        ],
        'console_scripts': [
            # 提供手动执行 hooks 的入口
            'mkdocs-document-dates-hooks=mkdocs_document_dates.hooks_installer:install'
        ],
    },
    package_data={
        'mkdocs_document_dates': [
            'hooks/*',
            'static/languages/*',
            'static/tippy/*',
            'static/core/*',
            'static/config/*'
        ],
    },
    python_requires=">=3.7",
)