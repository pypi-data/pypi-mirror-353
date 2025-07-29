from setuptools import setup, find_packages

setup(
    name="shutill",
    version="3.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "shutill=shutill.__main__:open_calc",
        ],
    },
    description="Open Windows Calculator from Python",
    author="Bat-sec",
    author_email="bat-sec1337@outlook.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.6",
)
