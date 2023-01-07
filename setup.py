from setuptools import find_packages, setup

VERSION = '0.0.1'
DESCRIPTION = 'Asynchronous InPost library'
LONG_DESCRIPTION = 'Asynchronous InPost package allowing you to manage existing incoming parcels without mobile app'

setup(
    name='inpost-python',
    packages=find_packages(),
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='loboda4450, mrkazik99',
    author_email='loboda4450@gmail.com, mrkazik99@gmail.com',
    maintainer='loboda4450',
    maintainer_email='loboda4450@gmail.com',
    keywords=['inpost', 'carrier', 'lockers'],
    url='https://github.com/IFOSSA/inpost-python',
    license='LGPL 2.1',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Framework :: aiohttp",
        "Intended Audience :: Developers",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ]
)
