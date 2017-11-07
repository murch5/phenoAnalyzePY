from distutils.core import setup
from plot_analyze.__init__ import __version__ as version

setup(
    name='plotanalyze',
    version=version,
    packages=['plot_analyze', 'plot_analyze.datatype'],
    url='',
    license='',
    author='Ryan',
    author_email='',
    description='Data analysis and plotting suite', requires=['matplotlib','pandas']
)
