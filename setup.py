from setuptools import find_packages, setup

setup(name='gradescope_mean',
      version='0.0.2',
      description='utility to average gradescope csv output to final grades',
      author='Matt Higger',
      author_email='matt.higger@gmail.com',
      url='https://github.com/matthigger/gradescope_mean',
      packages=find_packages(),
      package_data={'gradescope_mean': ['config.yaml']},
      install_requires=[
          'numpy',
          'pandas',
          'plotly',
          'pytest',
          'pyyaml']
      )
