import sys

from distutils.core import setup

if sys.version_info < (3,6):
    sys.exit('Python < 3.6 is not supported by doodle.')

setup(
    name='doodle',
    packages=['doodle'],
    version='1.0',
    description='A python framework for creating static images from dynamic content.',
    author='marika',
    author_email='marika@waifu.club',
    url='https://github.com/aoki-marika/doodle',
    download_url='https://github.com/aoki-marika/doodle/archive/1.0.tar.gz',
    keywords=['framework', 'image'],
    classifiers=[],
    install_requires=['pillow'],
)
