from setuptools import setup, find_packages

setup(name = "grailmud",
      version = "0.1a0",
      packages = find_packages(),

      install_requires = ['durus>=3.6', 'pyparsing'],

      author = "Sam Pointon",
      author_email = "free.condiments@gmail.com",
      description = "A Python MUD server",
      license = "GNU GPL",
      keywords = "mud server game online rpg mmorpg text adventure")
