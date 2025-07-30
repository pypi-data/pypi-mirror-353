from setuptools import setup, find_packages

try:
    with open("README.mv", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Command Line tool to process a text file and output the word frequency of its content."

setup(
    name='crgwordcounter',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'crgwordcounter=wordcounter_cli.cli:main',
        ],
    },
    author='CORG',
    author_email='rgz.claudio@gmail.com',
    description='Command Line tool to process a text file and output the word frequency of its content.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://git.epam.com/claudio_rodriguez1/test-automation/-/tree/main/test-automation/tips-and-tricks?ref_type=heads',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)