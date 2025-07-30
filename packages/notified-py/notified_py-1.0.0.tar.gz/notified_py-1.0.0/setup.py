from setuptools import setup, find_packages

setup(
  name='notified_py',
  version='1.0.0',
  packages=find_packages(),
  install_requires=[
    'requests==2.32.3'
  ],
)