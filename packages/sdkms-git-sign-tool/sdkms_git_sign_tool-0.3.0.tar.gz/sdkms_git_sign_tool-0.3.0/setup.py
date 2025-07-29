import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

NAME = "sdkms-git-sign-tool"

README = (HERE / "README.md").read_text()

VERSION = "0.3.0"

REQUIRES = [
    "sdkms>=4.35.0,<5.1.0",
    "gitpython>=3.1.44,<4.0.0",
    "PGPy~=0.6",
    "pyasn1~=0.4.8",
    "python-dateutil~=2.9.0",
    "cryptography~=36.0.0",
]

setup(
    name=NAME,
    version=VERSION,
    description="Fortanix DSM Git Sign Tool",
    author="Fortanix",
    author_email="support@fortanix.com",
    url="https://support.fortanix.com",
    keywords=["DSM", "SDKMS", "Fortanix DSM", "git", "sign-tool"],
    install_requires=REQUIRES,
    packages=find_packages(),
    entry_points={
        "console_scripts": ["sdkms-git-sign-tool=sdkms_git_sign_tool.__main__:main"]
    },
    include_package_data=True,
    long_description=README,
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Security :: Cryptography",
    ],
)
