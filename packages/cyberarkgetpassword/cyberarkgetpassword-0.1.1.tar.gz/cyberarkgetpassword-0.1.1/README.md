STEP 1: Project Structure
Ensure your package directory is structured like this:


common_utilities/
│
├── cyberarkgetpassword/
│   ├── __init__.py
│   └── cyberark_get_password_obj.py  # contains CyberArkPassword
│
├── setup.py
├── pyproject.toml  # recommended
├── README.md
└── LICENSE

STEP 2: Create Required Files
cyberarkgetpassword/__init__.py
Export your class:


from .cyberark_get_password_obj import CyberArkPassword

__all__ = ["CyberArkPassword"]
setup.py


from setuptools import setup, find_packages

setup(
    name="cyberarkgetpassword",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],  # Add dependencies if any
    author="Surendra Kumar",
    author_email="your_email@example.com",
    description="Utility to fetch CyberArk passwords",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cyberarkgetpassword",  # Optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
pyproject.toml (optional but recommended)

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

STEP 3: Build the Package
Install necessary tools:


pip install setuptools wheel
Then run:


python setup.py sdist bdist_wheel
You’ll see a dist/ folder with files like:


dist/
├── cyberarkgetpassword-0.1.0.tar.gz
└── cyberarkgetpassword-0.1.0-py3-none-any.whl

STEP 4: Register on PyPI
Go to https://pypi.org/account/register/ and create a free account.

Set up 2FA using Google Authenticator or similar.

Go to your account → API tokens → click Add API token.

Copy the token (starts with pypi-...) — you’ll need it in the next step.

STEP 5: Upload to PyPI
Install twine:


pip install twine
Then upload:


twine upload dist/*
When prompted:

Enter your username (usually your PyPI username)

Paste your API token (instead of a password)

STEP 6: Verify Your Package
Visit:


https://pypi.org/project/cyberarkgetpassword/
You should see your published package there.

STEP 7: Install from Anywhere
Now you (or anyone) can install it using:


pip install cyberarkgetpassword

🔄 To Update Later
Bump the version in setup.py (e.g., from 0.1.0 to 0.1.1)

Rebuild:


python setup.py sdist bdist_wheel
Re-upload:


twine upload dist/*
