from setuptools import setup, find_packages

setup(
    name='grizzel',
    version='0.1.2', 
    packages=find_packages(),
    install_requires=[
        'nltk',
        'beautifulsoup4',
    ],
    author='Ratul Sur',
    author_email='your@email.com',
    description='A simple text cleaning utility using NLTK and BeautifulSoup',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/grizzel/',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
