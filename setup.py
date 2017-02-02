from setuptools import setup

with open('README.rst') as fp:
    README = fp.read()

setup(
    name='gptools',
    version='0.1',
    author='Sviatoslav Abakumov',
    author_email='dust.harvesting@gmail.com',
    description='Guitar Pro clipboard tools',
    long_description=README,
    url='https://github.com/Perlence/gptools',
    download_url='https://github.com/Perlence/gptools/archive/master.zip',
    py_modules=['gptools'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'gptools = gptools.cli:cli',
        ],
    },
    install_requires=[
        'attrs',
        'click',
        'psutil',
        'pyguitarpro',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ]
)
