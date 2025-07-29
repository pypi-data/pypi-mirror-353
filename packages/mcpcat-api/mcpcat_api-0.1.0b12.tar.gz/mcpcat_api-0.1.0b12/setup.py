from setuptools import setup, find_packages

setup(
    name="mcpcat_api",
    version="0.1.0-beta.12",
    packages=find_packages(),
    install_requires=[
        "urllib3 >= 1.25.3",
        "python-dateutil",
        "pydantic>=1.10.5,<2",
    ],
)
