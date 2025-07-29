from setuptools import setup

setup(
    name="sqlgenx",
    version="0.1.11",
    py_modules=["sqlgenx"],
    description="Generate SQL INSERT from CSV or pandas DataFrame",
    author="ryohei-iwamoto",
    author_email="celeron5576@gmail.com",
    install_requires=[
        "pandas"
    ],
    python_requires=">=3.7",
)
