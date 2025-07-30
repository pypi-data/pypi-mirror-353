from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='fetch_paros_data',  # pip package name
    version='0.1.2',
    description='Fetch and process InfluxDB data from PAROS sensors',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ethan Gelfand',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'influxdb-client',
        'pytz',
        'pandas',
        'scipy'
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
)
