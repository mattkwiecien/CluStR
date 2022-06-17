from setuptools import setup

setup(
    name='clustr',
    version='1.0',
    description='This package calculates various scaling relations from cluster catalogs.',
    author='Paige, Jose, Spencer',
    author_email='',
    url='https://www.python.org/sigs/distutils-sig/',
    packages=['clustr'],
    install_requires=[
        'astropy', 'corner', 'PyPDF2', 'linmix', 'rpy2',
        'pyfiglet', 'numpy'
    ]
)