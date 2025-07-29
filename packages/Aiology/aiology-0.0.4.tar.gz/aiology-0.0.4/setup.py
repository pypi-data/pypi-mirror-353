from setuptools import setup , find_packages

with open("README.md","r") as file:
    readme = file.read()

setup(
    name="Aiology",
    version="0.0.4",
    author="Seyed Moied Seyedi (Single Star)",
    packages=find_packages(),
    install_requires=[
        "requests","pypdf","arabic-reshaper","python-bidi","setuptools","langchain-community==0.3.24",
        "langchain==0.3.25","sentence-transformers==4.1.0","langchain-text-splitters==0.3.8","chromadb==0.4.14"
    ],
    license="MIT",
    description="Ai library",
    long_description=readme,
    long_description_content_type="text/markdown"
)