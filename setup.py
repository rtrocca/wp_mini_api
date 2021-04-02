from setuptools import setup, find_packages
setup(name='wp_mini_api',
    version='0.1',
    description='A mini API to communicate with WordPress',
    packages=find_packages(),
    install_requires=[
        'slugify'
    ]
)
