from setuptools import setup, find_packages

setup(
    name='jerris-client',
    version=open('version.txt').read().strip(),
    author='Jerris',
    author_email='contact@syrtis.be',
    description='Jerris API Client for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        "pillow"
    ],
    python_requires='>=3.6',
)
