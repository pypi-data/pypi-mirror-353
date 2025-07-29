from setuptools import setup, find_packages

setup(
    name="kurzaj",
    version="0.16.0",
    packages=find_packages(),
    install_requires=[
        'Pillow'
    ],
    package_data={"":["**/*.jpg"]},
    author="meow",
    description="furry po edition",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://example.com/",  # Replace with your GitHub
    python_requires=">=3.6",
)
