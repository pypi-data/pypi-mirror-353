from setuptools import setup, find_packages

setup(
    name='minwei_tools',
    version='0.1.2',
    author='OUYANGMINWEI',
    author_email='wesley91345@gmail.com',
    description='Some useful tools for Python development',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/OuYangMinOa/minwei_tools',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

"""
python -m build
twine upload dist/*

"""