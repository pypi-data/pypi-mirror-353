from setuptools import setup, find_packages

setup(
    name='mtn-momo-sdk',
    version='0.1.5',
    description='MTN MoMo API Collection SDK for Python',
    author='Bruce Bagarukayo',
    author_email='bbagarukayo5@gmail.com',
    url='https://github.com/brucekyl/momo-sdk',
    packages=find_packages(),
    install_requires=['requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
