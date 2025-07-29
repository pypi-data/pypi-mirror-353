"""
Setup script untuk ArisDev Framework
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="arisdev",
    version="0.1.0",
    author="ArisDev",
    author_email="arisdev@example.com",
    description="A simple web framework for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arisdev/arisdev",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "werkzeug>=2.0.0",
        "jinja2>=3.0.0",
        "sqlalchemy>=1.4.0",
        "redis>=4.0.0",
        "bcrypt>=3.2.0",
        "pyjwt>=2.0.0",
        "schedule>=1.1.0",
        "websockets>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
    },
) 