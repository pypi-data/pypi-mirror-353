from setuptools import setup, find_packages

setup(
    name="blackspammerbd-termux",
    version="1.0.0",
    author="BLACK SPAMMER BD",
    description="Auto Telegram backup tool for Termux",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests"],
)
