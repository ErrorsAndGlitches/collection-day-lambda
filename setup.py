from setuptools import setup, find_packages

setup(
    name='collection-day-lambda',
    version='0.1',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.11, <4',
    url='',
    license='MIT License',
    author='ErrorsAndGlitches',
    author_email='',
    description='Lambda function to provide collection notifications',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['collection-day-lambda=cdl.__main__:main'],
    }
)
