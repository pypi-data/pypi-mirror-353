
from setuptools import setup, find_packages

setup(
    name='logbrain',
    version='0.1.1',
    packages=find_packages(),
    license='MIT',
    py_modules=['logbrain'],
    install_requires=[
        'transformers',
        'pytesseract',
        'Pillow',
        'requests'
    ],
    author='Maurya Allimuthu',
    author_email='catchmaurya@gmail.com',
    description='LogBrain - Smart log analyzer using symbolic logic and lightweight AI',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    url='https://github.com/catchmaurya/logbrain',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
