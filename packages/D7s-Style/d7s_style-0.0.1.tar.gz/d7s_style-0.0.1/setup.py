import setuptools

setuptools.setup(
    name="D7s-Style",
    version="0.0.1",
    author="DARK7STORM",
    author_email="darkstorm048@gmail.com",
    description="A small example package",
    long_description_content_type="text/markdown",
    url="https://github.com/DARK7STORM-D7S/D7s-Style.git",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
