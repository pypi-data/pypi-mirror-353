from setuptools import setup, find_packages

setup(
    name="misaa",
    version="1.0",
    packages=find_packages(),
    install_requires=["requests"],
    entry_points={
        "console_scripts": [
            "misaa=misaa.cli:main"
        ]
    },
    author="kuroh",
    description="Recherche OSINT rapide de pseudo.",
    python_requires=">=3.7",
)
