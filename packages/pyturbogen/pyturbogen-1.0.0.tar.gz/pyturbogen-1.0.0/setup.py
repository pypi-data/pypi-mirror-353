from setuptools import setup, find_packages
setup(
    name='pyturbogen',
    version='1.0.0',
    author='Gaurav Pandey',
    author_email='golupandey95207@gmail.com',
    description='A simple image generation library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Coder-Gaurav997/pyturbogen',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)