from setuptools import find_packages, setup

setup(name='gradescope_mean',
      description='utility to average gradescope csv output to final grades',
      author='Matt Higger',
      author_email='matt.higger@gmail.com',
      packages=find_packages(),
      package_data={'gradescope_mean': ['config.yaml']},
      install_requires=[
          'numpy',
          'pandas',
          'plotly',
          'pytest',
          'pyyaml']
      )
