from setuptools import setup, find_packages


setup(
    name='assetoolz',
    version='0.0.6',
    description='Web assets build system',
    author='Alexander Pyatkin',
    author_email='asp@thexyz.net',
    packages=find_packages('.'),
    install_requires=[
        'setuptools>=5.4',
        'sqlalchemy>=0.9,<1.0',
        'pyyaml>=3.11',
        'simplejson>=3.6,<4.0'
    ],
    url='https://github.com/aspyatkin/assetoolz',
    license='MIT',
    entry_points=dict(
        console_scripts=['assetoolz = assetoolz:main'])
)
