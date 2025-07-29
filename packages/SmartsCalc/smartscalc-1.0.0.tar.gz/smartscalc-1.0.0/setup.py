from setuptools import setup, find_packages

setup(
    name="SmartsCalc",
    version="1.0.0",
    description="A library to calculate mathematical equations from text input. مكتبة تتيح لك حساب المعادلات الرياضية التي في شكل نصي.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ryan Al-saidani",
    author_email="ryan.alsaidani@gmail.com",
    url="https://github.com/ryan-alsaidani/SmartsCalc",
    packages=find_packages(),
    python_requires='>=3.7',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Utilities",
        "Topic :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Natural Language :: Arabic",
        "Operating System :: OS Independent"
    ],
    keywords="calculator math equations text processing python",
    license="Custom License - All Rights Reserved",
    include_package_data=True,
    install_requires=[],
)
