from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="drf-authenticator",
    version="0.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django",
        "djangorestframework",
        "cryptography>=3.4.0",
    ],
    description="A reusable Django app for Token Authentication.",
    ong_description=long_description,
    long_description_content_type="text/markdown",
    author="Abhishek Vamja",
    author_email="abhishekvamja2518@gmail.com",
    url="https://github.com/Abhishek-vamja/drf_authenticator",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
