import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fgb-opram",                         # Unique package name on PyPI
    version="0.1.0",
    author="Bongjae Kwon",
    author_email="bongjae.kwon@snu.ac.kr",
    description="Fuzzy Granular-Ball and OPRAm-based spatial query answering framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bongjaekwon/FGB-OPRAm-SQAUE",
    license="MIT",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.6',
    install_requires=[
        "numpy>=1.19.0",
        "scipy>=1.5.0",
        "matplotlib>=3.3.0"
        # tkinter is part of the Python standard library
    ],
    entry_points={
        "console_scripts": [
            "fgb_opram_gui = fgb_opram.gui:main"
        ]
    }
)
