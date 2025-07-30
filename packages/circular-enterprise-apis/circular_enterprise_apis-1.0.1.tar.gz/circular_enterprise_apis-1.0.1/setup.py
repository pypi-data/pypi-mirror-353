from setuptools import setup, find_packages

setup(
    name='circular_enterprise_apis',
    version='1.0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'ecdsa',
    ],
    author='Danny De Novi',
    author_email='dannydenovi29@gmail.com',
    description='Official Circular API for Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/circular-protocol/Python-Enterprise-APIs',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
