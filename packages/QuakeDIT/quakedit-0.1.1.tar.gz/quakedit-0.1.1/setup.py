from setuptools import setup

setup(
    name="QuakeDIT",
    version="0.1.1",
    long_description="quakedit",
    long_description_content_type="text/markdown",
    packages=["quakedit"],
    install_requires=["numpy",  "h5py", "matplotlib", "pandas"],
)
