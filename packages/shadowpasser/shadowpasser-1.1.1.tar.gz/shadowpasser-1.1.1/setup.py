from setuptools import setup, find_packages

setup(
    name="shadowpasser",
    version="1.1.1",
    author="Team ShadowCryptics",
    description="IAMNEO Restriction Bypasser for RMKEC Students",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyQt5",
        "PyQtWebEngine",
    ],
    entry_points={
        "gui_scripts": [
            "shadowpasser=shadowpasser.app:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)