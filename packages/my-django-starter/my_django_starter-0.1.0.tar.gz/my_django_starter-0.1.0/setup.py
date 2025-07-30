from setuptools import setup, find_packages

setup(
    name="my-django-starter",
    version="0.1.0",
    author="Chandra Mohan Sah ",
    author_email="csah9628@gmail.com",
    description="A starter kit to quickly scaffold Django projects.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ChandraMohan-Sah/my-django-starter",  
    packages=find_packages(),
    include_package_data=True,
    install_requires=open("requirements.txt").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "mydjango=my_django_starter.main:main",  # For CLI
        ],
    },
    python_requires='>=3.6',
)
