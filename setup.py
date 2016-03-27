from setuptools import setup

setup(
    name='werewolf',
    version="0.1.0",

    install_requires = [
        'django >= 1.9, < 1.10', 
        'djangorestframework >= 3.3, < 3.4',
    ],

    author='Rolando Cruz',
    author_email='rolando.cruz21@gmail.com',
    license='MIT',
    keywords='werewolf'
)
