from setuptools import setup, find_packages

setup(
    name='etl_pipeline',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # list dependencies here
    ],
    entry_points={
        'console_scripts': [
            'etl_pipeline=my_etl_package.etl_pipeline:main',
        ],
    },
)
