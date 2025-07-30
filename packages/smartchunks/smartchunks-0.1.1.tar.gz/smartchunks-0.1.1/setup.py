
from setuptools import setup, find_packages

setup(
    name='smartchunks',
    version='0.1.1',
    description='Advanced Python chunking with stride, filtering, and expressions',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    author='Maurya Allimuthu',
    author_email='catchmaurya@example.com',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[],
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
