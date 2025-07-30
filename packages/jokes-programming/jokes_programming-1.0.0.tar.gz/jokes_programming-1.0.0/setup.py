from setuptools import setup, find_packages
from pathlib import Path

readme = Path("README.md").read_text(encoding="utf-8")

setup(
    name="jokes_programming",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["numpy"],
    entry_points={
        "console_scripts": [
            "jokes_programming=jokes_programming.run:run",
        ],
    },
    author="Ruan Narici",
    description="Piadas engraçadas sobre programação e dados.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/ruan-narici/jokes_about_programming",
    project_urls={
        "Source": "https://github.com/ruan-narici/jokes_about_programming",
        "Bug Tracker": "https://github.com/ruan-narici/jokes_about_programming/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    keywords=["piadas", "programação", "humor", "dados", "developer jokes"],
)
