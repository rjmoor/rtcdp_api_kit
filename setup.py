# setup.py

from setuptools import setup, find_packages

setup(
    name="rtcdp_api_kit",
    version="0.1.0",  # 🔥 Version early and often
    author="Rahm Moor",
    author_email="rahmind.consulting@rmoorind.com",  # TODO: Update with your email
    description="A modular API toolkit for accessing and controlling data in Adobe Experience Platform (AEP).",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rjmoor/rtcdp_api_kit",
    packages=find_packages(exclude=["tests*", "logs*", "_sql_files*", "_json_files*", "templates*"]),
    install_requires=[
        "requests>=2.31.0",
        "PyYAML>=6.0.1",
        "pandas>=2.2.2",
        # 👇 Add any other external libraries you use here
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",   # (Later bump to Beta/Production)
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",  # (or whatever license you prefer)
        "Programming Language :: Python :: 3.10",  # Match your real target Python version
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    include_package_data=True,
    zip_safe=False,
)
