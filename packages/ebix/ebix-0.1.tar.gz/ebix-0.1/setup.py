
from setuptools import setup, find_packages

setup(
    name='ebix',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'questionary'
    ],
    entry_points={
        'console_scripts': [
            'ebix=ebix.cli:cli',
        ],
    },
    author="Piyush Pal",
    description="A CLI to generate frontend/backend/full-stack starter projects",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/piyushirish/command-line-interface.git",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
