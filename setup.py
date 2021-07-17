from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='errutils',
      version='0.9',
      description='Elemental Reasoning reporting utilities',
      long_description=readme(),
      url='http://github.com/jasonmccsmith/errutils',
      author='Elemental Reasoning',
      author_email='jason@elementalreasoning.com',
      license='BSD-3',
      packages=['errutils'],
      install_requires=[
          'coloredlogs',
      ],
      include_package_data=True,
      zip_safe=False)
