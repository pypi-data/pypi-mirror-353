from setuptools import setup ,find_packages


setup(
    name='strtovar',
    version='0.1.1',
    author='chetan',
    author_email='chetansuthar734@gmail.com',
    description='converting string name to variable',
    long_description=open('README.md',encoding='utf-8').read(),
    packages=find_packages(),
    entery_point={'console_scripts':['strtovar.strtovar.main']},
    classifiers=[]



)