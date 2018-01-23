from setuptools import setup

setup(
    name='mwa_photometry',
    version='0.1',
    py_modules=['mwa_photometry'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
        'mwa_photometry=mwa_photometry'
    ]},
)