import setuptools

long_description = """
    This package facilitates
"""

setuptools.setup(
    name='etl_pipeline_ggn1_ase_g5',
    version='4.0',
    packages=setuptools.find_packages(),
    install_requires=['dill', 'fastapi', 'schedule', 'uvicorn', 'pandas'],
    entry_points={
        'console_scripts': [
            'etl_pipeline = etl_pipeline_ggn1_ase_g5:__main__',
        ]
    },
    description='Short description',
    long_description=long_description
)