from setuptools import setup, find_packages

setup(
    name="grainsy",  # Name of your library
    version="1.0.0",  # Version number
    description="Library for calculating grains on a chessboard",
    author="Vajo Sekulic",
    author_email="hello@bekindstudio.at",
    packages=find_packages(),  # Automatically find packages
    install_requires=[],  # List dependencies if any
    python_requires=">=3.11",  # Python version used in the library
)