from setuptools import setup, find_namespace_packages

setup(
    name='file-sorter',
    version='2.0',
    description='''A Python utility for organizing and sorting files into
                   categories based on file extensions''',
    url='https://github.com/alex-nuclearboy/goit-python-web-hw3-sorter.git',
    author='Aleksander Khreptak',
    author_email='alex.nuclearboy@gmail.com',
    license='MIT',
    packages=find_namespace_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'file-sorter=sorter.main:console_script',
        ],
    },
)
