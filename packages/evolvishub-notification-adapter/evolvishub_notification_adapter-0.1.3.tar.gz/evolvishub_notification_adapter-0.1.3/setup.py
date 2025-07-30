from setuptools import setup, find_packages

setup(
    name="evolvishub-notification-adapter",
    version="0.1.3",
    packages=find_packages(),
    install_requires=[
        "aiosqlite>=0.19.0",
        "pyyaml>=6.0.1",
    ],
    python_requires=">=3.7",
    author="Alban Maxhuni, PhD",
    author_email="a.maxhuni@evolvis.ai",
    description="A flexible notification system adapter for Evolvishub applications",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/evolvis/evolvishub-notification-adapter",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    extras_require={
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
) 