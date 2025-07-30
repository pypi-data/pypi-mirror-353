from setuptools import setup, find_packages

#Leer el contenido de README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hack4uLib",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Rodrigo Inzaurralde",
    description="Una biblioteca para consultar cursos de la academia hack4u.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://hack4u.io",
)
