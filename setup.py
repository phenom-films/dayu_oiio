from setuptools import setup

setup(
        name='dayu_oiio',
        version='0.2',
        packages=['dayu_oiio'],
        url='https://github.com/phenom-films/dayu_oiio',
        license='MIT',
        author='andyguo',
        author_email='andyguo@phenom-films.com',
        description='a python wrapper for OpenImageIO oiiotool.',
        long_description=open('README.rst').read(),
        classifiers=[
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: Implementation',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
        ],
)
