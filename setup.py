import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="globalfirepower-scraper",
    version="0.0.1",
    author="Mickaël Andrieu",
    author_email="mickael.andrieu@solvolabs.com",
    url="https://github.com/mickaelandrieu/global-firepower-scraper",
    description="Global FirePower Scraper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    py_modules=["globalfirepower"],
    package_dir={"":"globalfirepower/src"},
    install_requires=[
        "aiohttp==3.8.1",
        "asyncio==3.4.3",
        "bs4==0.0.1",
        "pandas==1.4.1",
        "requests==2.27.1",
        "lxml==4.8.0"
    ]
)