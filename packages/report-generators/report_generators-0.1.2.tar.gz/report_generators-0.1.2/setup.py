from setuptools import setup, find_packages

setup(
    name='report_generator',
    version='0.1.0',
    author='Antônio Marchese',
    author_email='devmarcheseantonio@gmail.com',
    description='A python package for reports generation.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/antonoiMarchese/my_package',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        # List your package dependencies here
    ],
)