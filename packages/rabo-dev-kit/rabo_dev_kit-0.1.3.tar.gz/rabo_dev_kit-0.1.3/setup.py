from setuptools import setup, find_packages

setup(
    name="rabo-dev-kit",
    version="0.1.3",
    packages=find_packages(),
    author="origin",
    author_email="cmeng.gao@gmail.com",
    description="",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)