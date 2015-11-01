"""Setup for uc_docker XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data.

    All of the files under each of the `roots` will be declared as package
    data for package `pkg`.

    """
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='ibm_docker-xblock_test',
    version='0.1',
    description='ibm_docker_test XBlock',   # TODO: write a better description.
    packages=[
        'ibm_docker_test',
    ],
    install_requires=[
        'XBlock',
        'paramiko',
        'docker-py',
    ],
    entry_points={
        'xblock.v1': [
            'ibm_docker_test = ibm_docker_test:IBMDockerTestXBlock',
        ]
    },
    package_data=package_data("ibm_docker_test", ["static", "public"]),
)
