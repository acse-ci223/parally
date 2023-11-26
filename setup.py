try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="parally",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Distributed computing over networks",
    long_descritpion="""
    This is a package for distribute functions over networks
    """,
    url="https://github.com/acse-ci223/parally",
    author="Chris Ioannidis",
    author_email="chris.ioannidis23@imperial.ac.uk",
    packages=["parally"],
)
