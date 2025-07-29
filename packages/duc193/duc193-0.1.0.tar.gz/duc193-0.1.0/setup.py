from setuptools import setup, find_packages

setup(
    name="duc193",
    version="0.1.0",
    description="Cho em con mã nè . . .",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Duc193",
    author_email="actaccaribe2006@gmail.com",
    url="https://github.com/derive206",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
