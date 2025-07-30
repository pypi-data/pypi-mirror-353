from setuptools import setup, find_packages

setup(
    name="mctech_discovery",
    version="1.1.15",
    packages=find_packages(
        include=["mctech_discovery**"],
        exclude=["*.test"]
    ),
    install_requires=["log4py", "netifaces",
                      "py_eureka_client", "httpx",
                      "mctech-actuator", "mctech-core", "websocket-client"]
)
