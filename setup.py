from setuptools import setup, find_packages
setup(name='wp_mini_api',
    version='0.1.2',
    description='A mini API to communicate with WordPress',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25',
        'slugify'
    ]
)
