from setuptools import setup, find_packages

setup(
    name="a-max-product-limited",
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    author='Avinash S',
    author_email='avinash.s@gmail.com',
    description='A package containing company information and 10 products',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Avinash8055/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires=">=3.7"
)