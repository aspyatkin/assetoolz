from setuptools import setup, find_packages

install_requires = [
    "sqlalchemy"
]

setup(
    name='assetoolz',
    version='0.1',
    description='Web assets preprocessor',
    author='Alexander Pyatkin',
    author_email='A.S.Pyatkin@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    data_files=[],
    install_requires=install_requires
)
