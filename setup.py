from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(name='TSO500Reporter',
      version='0.1.0',
      description='Parsing and reporting library for the TSO500 app. Works \
            with CombinedVariantOutput.tsv files and allows data \
            manipulation and report generation.',
      long_description=readme(),
      url='http://github.com/spaul91/TSO500Reporter',
      author='Sophie Paul',
      author_email='sophie.paul@addenbrookes.nhs.uk',
      license='MIT',
      packages=['tso500reporter'],
      include_package_data=True,
      install_requires=[
          "jinja2",
          "matplotlib",
          "pandas",
          "seaborn",
          "weasyprint",
          ],
      zip_safe=False)
