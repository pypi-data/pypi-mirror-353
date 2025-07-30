from setuptools import setup, find_packages

setup(
    setup_requires=['setuptools>=61'],
    name='pycommonPK',
    version='0.1.0',
    author='xystudio',
    author_email='173288240@qq.com',
    requires=[],
    description='Some python common packages.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.9',
    license=open('LICENSE').read(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords=['science', "debug", 'pyplus', 'tools', 'python'],
    install_requires=[],
    extras_require={
        'dev': [],
    },
    packages=find_packages(),
    url='https://github.com/xystudio889/pycommonPK',
)
