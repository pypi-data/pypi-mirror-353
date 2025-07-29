import setuptools


with open("README.md", "r") as f:
    long_description = f.read()


setuptools.setup(
    name="st-clipboard",
    version="0.0.1",
    author="Haloroute",
    author_email="quangtuyensctn@gmail.com",
    description="A lightweight clipboard copy utility for Streamlit, supporting both HTTP and HTTPS environments seamlessly.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Haloroute/st-clipboard",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
