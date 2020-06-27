import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dennis-mud-seisatsu", # Replace with your own username
    version="0-prealpha",
    author="Michael D. Reiley",
    author_email="seisatsu@seisat.su",
    description="Dennis MUD Muiltiplayer Text Adventure Sandbox Engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seisatsu/Dennis",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)
