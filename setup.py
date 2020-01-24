from setuptools import find_packages, setup

setup(
    name='dojograder',
    version='0.0.1',
    license='3-clause BSD',
    author='Jason Kuruzovich',
    author_email='kuruzj@rpi.edu',
    description='Lightweight autograder for notebooks',
    packages=find_packages(),
    install_requires=[
        'git+https://github.com/AnalyticsDojo/Gofer-Grader',
        'pandas',
        'bs4',
        'pytest-cov'
    ]
)
