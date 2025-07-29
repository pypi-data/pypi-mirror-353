from setuptools import setup, find_packages

setup(
    name='skyto',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'skyto=skyto.cli:main',
        ],
    },
    author='Tshinkola',
    description='Skyto, un langage en lingala pour apprendre la programmation et faire de l’IA',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
