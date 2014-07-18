from setuptools import setup, find_packages


setup(
    name='assetoolz',
    version='0.0.2',
    description='Web assets build system',
    author='Alexander Pyatkin',
    author_email='asp@thexyz.net',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    data_files=[],
    install_requires=[
        'setuptools',
        'sqlalchemy>=0.9,<1.0',
        'pyyaml>=3.11',
        'simplejson>=3.5,<3.6'
    ],
    platforms=['any'],
    url='https://github.com/aspyatkin/assetoolz',
    license='MIT'
)
