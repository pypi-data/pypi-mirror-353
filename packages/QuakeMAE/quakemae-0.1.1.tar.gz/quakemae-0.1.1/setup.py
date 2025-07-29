from setuptools import setup

setup(
    name="QuakeMAE",
    version="0.1.1",
    long_description="QuakeMAE",
    long_description_content_type="text/markdown",
    packages=["quakemae"],
    install_requires=["numpy",  "h5py", "matplotlib", "pandas"],
)
