"""
    setup script for the Docker Monitor
"""
from setuptools import find_packages, setup

with open("requirements.txt", encoding="utf-8") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

setup(
    name="monitor_docker",
    version="1.0",
    description="Monitor docker containers",
    packages=find_packages(),
    install_requires=requirements,
    test_suite="tests",
    # include_package_data: to install data from MANIFEST.in
    include_package_data=True,
    scripts=["scripts/monitor_docker-run"],
    zip_safe=False,
)
