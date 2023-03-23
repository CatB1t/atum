from setuptools import setup, find_packages

setup(
    name='atum',
    packages=find_packages(),
    package_dir={"atum": "atum"},
    entry_points={'console_scripts': ['atum = atum.__main__:main']}
)