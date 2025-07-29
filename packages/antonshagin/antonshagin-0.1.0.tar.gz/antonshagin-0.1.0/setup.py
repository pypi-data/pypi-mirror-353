from setuptools import setup, find_packages

setup(
    name='antonshagin',          # уникальное имя вашей библиотеки
    version='0.1.0',
    description='My asyncio-like library',
    author='Ваше имя',
    author_email='email@example.com',
    packages=find_packages(),
    python_requires='>=3.6',
)