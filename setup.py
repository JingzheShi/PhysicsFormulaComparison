import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
  name = 'gradePhyX',         # How you named your package folder (MyLib)
  packages = setuptools.find_packages(),   # Chose the same as "name"
  version = '0.0.8',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = '(1) an Engine to compare two Equations supporting Physics Quantities (i.e. constants, units, substitutions, etc.); and (2) an efficient implementation for grading a bunch of students answers to a bunch of Physics problems (whose scores are defined with tree-based structures), with multiprocessing support.',   # Give a short description about your library
  author = 'gradePhyX authors',                   # Type in your name
  author_email = 'sjzworking@outlook.com',      # Type in your E-Mail
  url = 'https://github.com/JingzheShi/PhysicsFormulaComparison',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/JingzheShi/PhysicsFormulaComparison/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['physics', 'sympy', 'formula comparison'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'sympy==1.13',
          'antlr4-python3-runtime==4.11',
          'numpy==2.1.2',
          'stopit==1.1.2',
          'regex',
          'tqdm',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
  ],
)