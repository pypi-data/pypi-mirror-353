from setuptools import setup, find_packages

setup(
    name='aira_cli',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'aira=aira_cli.main:main',
        ],
    },
    install_requires=[
        # List your dependencies here
    ],
    author='Your Name',
    author_email='your.email@example.com',
    description='AIRA CLI for managing a home server and the AIRA AI Platform',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/aira_cli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)