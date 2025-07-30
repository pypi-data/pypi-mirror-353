from setuptools import setup, find_packages

setup(
    name='skill-anvil-core-services',  
    version='0.1.4',
    packages=find_packages(include=["core_services", "core_services.*"]),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
    ],
    description='Reusable service layer for Django apps',
    author='Fodor Robert Stefan',
    author_email='robifodor1234576@yahoo.com',
    license='MIT',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)
