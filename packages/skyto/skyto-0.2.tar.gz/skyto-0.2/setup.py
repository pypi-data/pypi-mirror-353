from setuptools import setup, find_packages

setup(
    name='skyto',
    version='0.2',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'skyto=skyto.cli:main',
        ],
    },
    author='Lanscky Tshinkola',
    description='Skyto, un langage de programmation en lingala, pour apprendre la programmation et faire de l’IA',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
