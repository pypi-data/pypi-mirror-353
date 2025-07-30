from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-sql-query-logger",
    version="1.0.0",
    author="Aakash Pandit",
    author_email="aakashpandit366@gmail.com",
    description="A simple Django SQL Query Middleware package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aakash-Pandit/django-sql-query-logger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
    ],
    keywords="django middleware",
    project_urls={
        "Bug Reports": "https://github.com/Aakash-Pandit/django-sql-query-logger/issues",
        "Source": "https://github.com/Aakash-Pandit/django-sql-query-logger",
    },
)