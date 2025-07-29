from setuptools import setup, find_packages

setup(
    name='spotify-preview-finder',
    version='1.0.0',
    description='Get Spotify song preview URLs using Spotipy and web scraping',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Sonu Sahu',
    author_email='sonusahu050502@gmail.com',
    url='https://github.com/sonusahu05/spotify-preview-finder',
    packages=find_packages(),
    install_requires=[
        'spotipy>=2.23.0',
        'python-dotenv>=1.0.0',
        'beautifulsoup4>=4.12.3',
        'requests>=2.31.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
    python_requires='>=3.7',
)