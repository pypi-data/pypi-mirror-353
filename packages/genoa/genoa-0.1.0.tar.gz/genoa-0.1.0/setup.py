from setuptools import setup, find_packages

setup(
    name='genoa',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'torch>=2.5.1',
        'rich>=14.0.0'
    ],
    author='MrPsyghost',
    author_email='shivaypuri2000@gmail.com',
    summary='A powerful training algorithm for Neural Networks which works on Evolution and Genetics.'
)