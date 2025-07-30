from setuptools import setup, find_packages

setup(
    name="DecoLogger",
    version="0.0.1",
    description="It is the DecoLogger",
    author="chogamy",
    author_email="gamy0315@gmail.com",
    url="https://github.com/chogamy/DecoLogger",
    install_requires=[],
    packages=find_packages(exclude=[]),
    keywords=["logger", "decorator", "time", "error"],
    python_requires=">=3.6",
    package_data={},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
