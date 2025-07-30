from setuptools import setup, find_packages

setup(
    name="documenter",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=["markdown"],
    python_requires=">=3.6",
    author="xystudio",
    author_email="173288240@qq.com",
    description="Easy to load a markdown document and show it.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/xystudio889/documenter",
    include_package_data=True,
    entry_points={"console_scripts": [
        "documenter = documenter:main"
    ]
    },
    extras_require={
        "dev": []
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ], 
    keywords = ["load document", "document", "documenter", "markdown"]
)
