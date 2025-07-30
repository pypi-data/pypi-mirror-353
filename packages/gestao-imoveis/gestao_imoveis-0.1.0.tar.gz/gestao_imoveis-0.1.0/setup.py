from setuptools import setup, find_packages
from os import path

working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gestao_imoveis',
    version='0.1.0',
    url='https://github.com/silvagui04/GestaoImoveis/blob/main/Gestão_de_Imóveis.ipynb',
    author='Guilherme Silva, Gonçalo Tavares, João Maia, Vasco Azevedo',
    author_email='seu@email.com',
    description='Ferramenta para gestão de imóveis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
)