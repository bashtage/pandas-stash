from setuptools import setup, find_packages

setup(
    name='pandas-stash',
    version='0.9.9',
    packages=find_packages(),
    package_dir={'pandas_stash': './pandas_stash'},
    license='NSCA',
    author='Kevin Sheppard',
    url='https://github.com/bashtage/pandas-stash',
    long_description=open('README.md').read()
)


