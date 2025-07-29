from setuptools import setup

setup(
    name="QuakeClip",
    version="0.1.1",
    long_description="quakeclip",
    long_description_content_type="text/markdown",
    packages=["quakeclip"],
    install_requires=["numpy",  "h5py", "matplotlib", "pandas"],
)
