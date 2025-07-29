from setuptools import setup, find_packages

setup(
    name="awesomeff2",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "awesomeff2": ["bin/*"],  # Include binary files
    },
    description="wraps FFMPEG. see FFMPEG license"
)

