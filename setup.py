import re

from setuptools import find_packages, setup

with open("odb_tui/__init__.py") as f:
    version = re.search(r'__version__\s*=\s*"(.+?)"', f.read()).group(1)

setup(
    name="odb-tui",
    version=version,
    description="OBD-II diagnostic TUI",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "textual>=8.0.1",
        "obd>=0.7.3",
        "pyserial>=3.5",
    ],
    extras_require={
        "test": ["pytest>=7.0", "pytest-mock>=3.10"],
        "dev": ["pytest>=7.0", "pytest-mock>=3.10", "ruff>=0.4", "mypy>=1.10"],
    },
    entry_points={
        "console_scripts": [
            "odb-tui=odb_tui.__main__:main",
        ],
    },
)
