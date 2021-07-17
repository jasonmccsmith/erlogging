from setuptools import setup

setup(name='errutils',
      version='0.9',
      description='Elemental Reasoning reporting utilities',
      url='http://github.com/jasonmccsmith/errutils',
      author='Elemental Reasoning',
      author_email='jason@elementalreasoning.com',
      license='BSD-3',
      packages=['errutils'],
      install_requires=[
          'coloredlogs',
      ],
      zip_safe=False)
