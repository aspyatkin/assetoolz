from setuptools import setup, find_packages

install_requires = [
    'sqlalchemy'
]

setup(
    name='assetoolz',
    version='0.0.0',
    description='Web assets build system',
    author='Alexander Pyatkin',
    author_email='asp@thexyz.net',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    data_files=[],
    install_requires=['setuptools', 'sqlalchemy', 'pyyaml'],
    url='http://pypi.python.org/pypi/assetoolz',
    license='MIT'
)
