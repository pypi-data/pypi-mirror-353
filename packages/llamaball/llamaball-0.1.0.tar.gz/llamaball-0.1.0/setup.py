from setuptools import setup, find_packages

setup(
    name="llamaball",
    version="0.1.0",
    description="Accessible document chat and RAG system (Ollama backend)",
    author="Luke Steuber",
    author_email="luke@example.com",
    packages=find_packages(),
    install_requires=[
        "typer[all]",
        "ollama",
        "numpy",
        "tiktoken",
        "prompt_toolkit",
        "markdown-it-py",
        "tqdm",
        "rich"
    ],
    entry_points={
        "console_scripts": [
            "llamaball=llamaball.cli:main"
        ]
    },
    python_requires=">=3.8",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=open("README.md", "r", encoding="utf-8").read() if open("README.md", "r", encoding="utf-8") else "",
    long_description_content_type="text/markdown",
) 