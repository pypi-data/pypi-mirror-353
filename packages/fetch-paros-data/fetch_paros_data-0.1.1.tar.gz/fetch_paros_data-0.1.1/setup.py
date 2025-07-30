from setuptools import setup, find_packages

setup(
    name='fetch_paros_data',  # pip package name
    version='0.1.1',
    description='Fetch and process InfluxDB data from PAROS sensors',
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
)
