from setuptools import setup, find_packages

with open("README.md","r") as f:
    description = f.read()

setup(
    name='pypi-indices-api',
    version='0.3',
    description = 'A Python package to get the latest indices from the Indices-API',
    author = 'zylalabs',
    author_email = 'hello@zylalabs.com',
    url = 'https://github.com/Zyla-Labs/pypi-indices-api',
    keywords = ['indices-api', 'precious Indicesapi',  'Indicesapi', 'Indices', 'precious Indices' , 'gold' , 'silver', 'Platinum', 'Palladium', 'Ruthenium', 'Rhodium', 'forex data', 'rates', 'money', 'usd', 'eur', 'btc', 'forex api', 'gbp to usd', 'gbp to eur', 'eur to usd', 'api', 'currency api', 'exchange rate api', 'get currency rates api', 'currency rates php', 'usd to eur api','copper','nickel','aluminium','TIN', 'Zinc'],
    packages=find_packages(),
    install_requires=[
        
    ],
    long_description=description,
    long_description_content_type="text/markdown",
)