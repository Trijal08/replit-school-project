#from distutils.core import setup, find_packages
from distutils.core import setup
from setuptools import find_packages
#from gwesmap.config import Configuration

setup(
    name='gwesmap',
    version="0.0.1",
    author="Trijal Saha",
    author_email="trijal.saha@student.tdsb.on.ca",
    packages=find_packages(),  # Use find_packages to automatically find packages
    #entry_points={
    #    'console_scripts': [
    #        'gwesmap = gwesmap'
    #    ]
    #},
    license='GNU GPLv3',
    scripts=['bin/gwesmap'],
    description='George Webster Elementary School Map',
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3"
    ]
)
