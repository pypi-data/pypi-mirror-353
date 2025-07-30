from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="excluir-emails-gmail",
    version="1.1.0",
    author="Danilo Agostinho",
    author_email="danilodev.silva@gmail.com",
    description="A Python tool to batch delete Gmail emails based on sender lists",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daniloagostinho/excluir-emails-gmail-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications :: Email",
    ],
    python_requires=">=3.10",
    install_requires=[
        "google-auth>=2.21.0",
        "google-auth-oauthlib>=1.0.0",
        "google-auth-httplib2>=0.1.0",
        "google-api-python-client>=2.92.0",
        "rich>=13.4.2",
        "openpyxl",
        "numpy",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "excluir-emails-gmail=app:main",
        ],
    },
) 