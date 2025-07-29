from setuptools import setup, find_packages

setup(
    name='pypi_all_names',
    version='1.0.0',
    author='Jeong Gaon',
    author_email='gokirito12@gmail.com',
    description='Library to get all package names registered with PyPI at once!',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/gaon12/pypi_all_names',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'pypi-all-names = pypi_all_names.cli:main'
        ]
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    license='MIT',
)
