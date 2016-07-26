from distutils.core import setup


setup(name="datadog-logger",
      version="0.1.0",
      description="Python logging handler for DataDog events",
      url="https://github.com/ustudio/datadog-logger",
      packages=["datadog_logger"],
      install_requires=["datadog"])
