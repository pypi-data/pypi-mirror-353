from setuptools import setup, find_packages

setup(
    name="awesomeff",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "my_awesome_package": ["bin/*"],  # Include binary files
    },
)

