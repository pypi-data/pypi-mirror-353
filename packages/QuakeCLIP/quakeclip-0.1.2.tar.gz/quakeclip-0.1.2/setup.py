from setuptools import setup

setup(
    name="QuakeCLIP",
    version="0.1.2",
    long_description="quakeclip",
    long_description_content_type="text/markdown",
    packages=["quakeclip"],
    install_requires=["numpy",  "h5py", "matplotlib", "pandas"],
)
