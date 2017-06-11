from distutils.core import setup
from plotanalyze.__init__ import __version__ as version

setup(
    name='plotanalyze',
    version=version,
    packages=['plotanalyze', 'plotanalyze.datatype'],
    url='',
    license='',
    author='Ryan',
    author_email='',
    description='Data analysis and plotting suite', requires=['matplotlib','pandas']
)
