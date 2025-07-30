"""
author: wang ying
created time: 
intro:  python38
file:
"""

from setuptools import setup, find_packages

setup(
    name="RektecUUID",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        # 在这里列出你的库所需的其他Python包

    ],

    author="cacaowang",
    author_email="cacaowang@rektec.com.cn",
    description="Dailylogger deal for Rektec.co.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/yourusername/my-awesome-package",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)