import sys
from codecs import open
from os import path
from setuptools import setup, find_packages

install_requires = [
    'grpcio',
    'grpcio-tools',
    'googleapis-common-protos'
]
exclude_packages = ['tests']

MAJOR = sys.version_info[0]
MINOR = sys.version_info[1]

# only include the async grpc client for python 3.6+
if MAJOR == 3 and MINOR >= 6:
    install_requires.append('aiogrpc')
else:
    # exclude the async_client
    exclude_packages.append('*.async')

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lndgrpc',
    packages=find_packages(exclude=exclude_packages),
    install_requires=install_requires,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4',
    version='0.1.3',
    description='An rpc client for LND (lightning network deamon)',
    long_description=long_description,
    author='Adrien Emery',
    author_email='adrien.emery@gmail.com',
    url='https://github.com/adrienemery/lnd-grpc-client',
    download_url='https://github.com/adrienemery/lnd-grpc-client/archive/0.1.1.tar.gz',
    keywords=['lnd', 'lightning-network', 'bitcoin', 'grpc', 'rpc', 'async'],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
