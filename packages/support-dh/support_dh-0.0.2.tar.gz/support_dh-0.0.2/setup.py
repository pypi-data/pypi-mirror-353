import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="support-dh",
    version="0.0.2",
    author="astatine",
    author_email="astatine.147@gmail.com", 
    description="decorate text, etc", 
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/astatinegithub/support-dh.git",
    install_requires=[ 
    "matplotlib>=3.5.2", 
    "numpy>=1.21.5", 
    "pandas>=1.4.4", 
    "setuptools>=63.4.1", 
    ],
    include_package_data=True,
    packages = setuptools.find_packages(), 
    python_requires=">=3.9.13", 
)