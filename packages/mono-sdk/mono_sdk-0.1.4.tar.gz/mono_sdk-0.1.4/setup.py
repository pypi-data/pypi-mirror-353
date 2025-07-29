from setuptools import setup, find_packages

setup(
    name="mono-sdk",  # changed from mono-connect
    version="0.1.4",  # Incremented version
    description="Python SDK for Mono APIs (Connect, Customer, Directpay, Lookup)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Eze Israel John",
    author_email="ezeisraeljohn@gmail.com",
    url="https://github.com/ezeisraeljohn/mono-sdk",  # update if you change the repo name
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests>=2.20.0"],
    python_requires=">=3.6",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Source": "https://github.com/ezeisraeljohn/mono-sdk",  # update if you change the repo name
        "Documentation": "https://github.com/ezeisraeljohn/mono-sdk#readme",
    },
)
