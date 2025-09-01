from setuptools import setup, find_packages
from types import List

def get_requirements(file_path: str) -> List[str]:
    with open(file_path, "r") as file_obj:
        return [line.strip() for line in file_obj if line.strip()]

setup(
    name="Transactions Analysis",
    version="0.0.1",
    author="SunilKuBehera",
    author_email="sunil050@gmail.com",
    packages=find_packages(),
    install_requires=(get_requirements('requirements.txt'))
)