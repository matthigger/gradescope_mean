from setuptools import find_packages, setup

setup(name='mean_scope',
      description='utility to average gradescope csv output to final grades',
      author='Matt Higger',
      author_email='matt.higger@gmail.com',
      packages=find_packages(),
      install_requires=[
          'numpy',
          'pandas',
          'plotly',
          'pytest',
          'pyyaml',]
      )
