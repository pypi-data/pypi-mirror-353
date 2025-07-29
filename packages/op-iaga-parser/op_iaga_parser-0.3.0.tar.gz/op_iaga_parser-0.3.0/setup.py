from setuptools import setup, find_packages

setup(
    name='op_iaga_parser',
    version='0.3.0',
    description='Library for downloading and parsing Op and IAGA-2002 scientific data formats',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='31iwnl',
    author_email='xhispeco2018@gmail.com',
    url='https://github.com/31iwnl/op_parser',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.7',
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
