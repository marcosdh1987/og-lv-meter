from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="modbus_adv_toolbox",
    version="0.10.0",
    author="Marcos E Soto",
    author_email="marcos.esteban.soto@gmail.com",
    description="LLM Bench Toolbox",
    url="git@github.com:marcosdh1987/og-lv-meter.git",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    # install req from requirements.txt
    install_requires=[
        req for req in open("requirements.txt").read().split("\n") if req
    ],
)
