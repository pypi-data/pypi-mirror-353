from setuptools import setup, find_packages

setup(
    name='studentid_2401138',
    version='0.1.1',
    description='A simple package that shows my student ID',
    author='Sabin',
    author_email='sabin@dsu.ac.kr',
    packages=find_packages(),
    install_requires=[],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
