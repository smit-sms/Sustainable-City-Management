import setuptools

setuptools.setup(
    name='etl_pipeline_ggn1_ase_g5',
    version='0.0.1',
    packages=setuptools.find_packages(),
    install_requires=['dill', 'fastapi', 'schedule', 'uvicorn'],
    entry_points={
        'console_scripts': [
            'etl_pipeline = etl_pipeline_ggn1_ase_g5:__main__',
        ]
    }
)
