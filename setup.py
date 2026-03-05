from setuptools import setup, find_packages

setup(
    name="odb_read",
    version="0.1.0",
    description="OBD-II vehicle diagnostic TUI with UDS scanning",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "obd>=0.7.3",
        "pyserial>=3.5",
        "textual>=8.0.1",
        "rich>=14.3.3",
    ],
    extras_require={
        "graph": ["pandas", "numpy", "matplotlib"],
        "test": ["pytest>=7.0", "pytest-mock>=3.10"],
        "dev": ["pytest>=7.0", "pytest-mock>=3.10", "ruff>=0.4", "mypy>=1.10"],
    },
    entry_points={
        "console_scripts": [
            "odb-read=odb_read.__main__:main",
            "odb-graph=odb_read.services.graph:main",
        ],
    },
)
