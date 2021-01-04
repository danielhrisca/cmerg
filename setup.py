''' This file allows pip to create a wheel for the cmerg package. '''


from setuptools import setup
from pathlib import Path

from cmerg import __version__


HERE = Path(__file__)
REPO = HERE.parent
README = REPO / 'README.md'


if not README.exists():
    raise FileNotFoundError('README.md must missing in top directory')


setup(
    name='cmerg',
    version=__version__,
    description='Python parser for CarMaker ERG files.',
    long_description=README.read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/danielhrisca/cmerg',
    author='Daniel Hrisca',
    author_email='daniel.hrisca@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='carmaker erg development',
    packages=['cmerg'],
    # Because of pathlib it has to be >=3.4 and ~ is because we are not
    # committing to support python4.
    # See: https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires='~=3.4',
    install_requires=['asammdf', 'numpy'],
)
