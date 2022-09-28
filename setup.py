import subprocess
from setuptools import setup, find_packages

inception2corpus_version = subprocess.run(['git', 'describe', '--tags'], stdout=subprocess.PIPE).stdout.decode("utf-8").strip()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name="inception2corpus",
    version=inception2corpus_version,
    author='Lucas Terriel',
    license='MIT',
    description='A CLI for retrieving a corpus annotated with named entities '
                'from INCEpTION to an archived, reusable and versionable corpus.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/NER4Archives-project/inception2corpus-CLI',
    py_modules=['inception2corpus', 'i2c_lib'],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires='>=3.7',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        inception2corpus=inception2corpus:main
    """
)
