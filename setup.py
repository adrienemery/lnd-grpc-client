from setuptools import setup
setup(
    name='lndgrpc',
    packages=['lndgrpc'],
    install_requires=[
        'grpcio-tools',
        'grpcio',
        'aiogrpc',
        'googleapis-common-protos'
    ],
    version='0.1.0',
    description='An rpc client for LND (lightning network deamon)',
    author='Adrien Emery',
    author_email='adrien.emery@gmail.com',
    url='https://github.com/adrienemery/lnd-grpc-client',
    download_url='https://github.com/adrienemery/lnd-grpc-client/archive/0.1.tar.gz',
    keywords=['lnd', 'lightning-network', 'bitcoin', 'grpc', 'rpc', 'async'],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
