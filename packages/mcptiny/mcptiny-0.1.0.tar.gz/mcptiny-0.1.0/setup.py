from setuptools import setup, find_packages

setup(
    name="mcptiny",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastmcp>=0.1.0",  # MCP 服务器依赖
    ],
    entry_points={
        "console_scripts": [
            "mcptiny=mcptiny.main:main",
        ],
    },
    author="Livingstone",
    author_email="livingstone.guo@hotmail.com",
    description="A tiny MCP server example",
    long_description="A minimal MCP server implementation using FastMCP",
    long_description_content_type="text/markdown",
    url="https://github.com/lvst-gh/mcptiny",
    classifiers=[
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
)
