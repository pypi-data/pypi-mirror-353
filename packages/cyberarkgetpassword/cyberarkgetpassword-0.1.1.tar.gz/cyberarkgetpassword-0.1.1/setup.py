from setuptools import setup, find_packages

setup(
    name="cyberarkgetpassword",
    version="0.1.1",
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
