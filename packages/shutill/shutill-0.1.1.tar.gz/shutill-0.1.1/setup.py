from setuptools import setup, find_packages

setup(
    name='shutill',
    version='0.1.1',
    author='Bat-sec',
    author_email='bat-sec1337@outlook.com',
    description='A small utility library for shutdown-related messages',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Bat-sec/shutill',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
