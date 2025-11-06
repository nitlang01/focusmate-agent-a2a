from setuptools import setup, find_packages

setup(
    name="focusmate-agent-a2a",
    version="0.1.0",
    packages=find_packages(include=["agents", "models"]),
    install_requires=[],
)