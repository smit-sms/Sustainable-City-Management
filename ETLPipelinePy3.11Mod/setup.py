import setuptools
from pathlib import Path

# read the contents of the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name='etl_pipeline_ggn1_ase_g5',
    version='4.1',
    packages=setuptools.find_packages(),
    install_requires=['dill', 'fastapi', 'schedule', 'uvicorn', 'pandas'],
    entry_points={
        'console_scripts': [
            'etl_pipeline = etl_pipeline_ggn1_ase_g5:__main__',
        ]
    },
    long_description=long_description,
    long_description_content_type='text/markdown'
)
