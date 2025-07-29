from setuptools import setup, find_packages

setup(
    name='smtp-email-validator',
    version='0.1.1',
    description='Comprehensive email verification tool using regex, MX and SMTP checks',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Nworah Chimzuruoke Gabriel',
    author_email='your.email@example.com',
    url='https://github.com/Nworah-Gabriel/emailverifier',
    packages=find_packages(),
    install_requires=[
        'dnspython',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
