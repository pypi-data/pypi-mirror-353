from setuptools import setup, find_packages

setup(
    name="PyCoreEngine",
    version="0.1.0",
    description="A simple game engine built with PyGame",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="onepackage",
    author_email="umyashinderu@example.com",
    url="https://github.com/yourusername/pyengine",
    packages=find_packages(),
    install_requires=[
        'pygame>=2.0.0',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    keywords='game-engine pygame',
)