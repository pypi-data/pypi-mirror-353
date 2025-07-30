from setuptools import setup, find_packages

setup(
    name="mcpcat_api",
    version="0.1.2",
    packages=find_packages(),
    install_requires=[
        "urllib3>=1.25.3",
        "python-dateutil",
        "pydantic>=2.0.0,<3",
    ],
)
