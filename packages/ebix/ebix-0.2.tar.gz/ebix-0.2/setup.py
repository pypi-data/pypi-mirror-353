from setuptools import setup, find_packages

setup(
    name="ebix",
    version="0.2",
    packages=find_packages(), 
    include_package_data=True,
    install_requires=[
        "click",
        "questionary"
    ],
    entry_points={
        "console_scripts": [
            "ebix=ebix.cli:cli" 
        ],
    },
)
