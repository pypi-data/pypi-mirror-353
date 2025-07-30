from setuptools import setup, find_packages

setup(
    name="CrayonLogger",
    version="1.0.0",
    author="Leonardo Nery",
    author_email="leonardonery616@gmail.com",
    description="Um logger colorido com interface gráfica em Tkinter e suporte a decoradores.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
    ],
    python_requires=">=3.6",
    install_requires=[],
)
