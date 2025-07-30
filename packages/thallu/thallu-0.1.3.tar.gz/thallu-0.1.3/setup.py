from setuptools import setup , find_packages

with open("README.md" , "r") as f:
    description = f.read()

setup(
    name='thallu',
    version='0.1.3',
    packages=find_packages(),
    install_requires = [],
    entry_points = {
        'console_scripts' : [
            'thallu = thallu:main',
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown",
    )