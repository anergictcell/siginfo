import setuptools
import siginfo

with open("README.rst", "r") as fh:
    long_description = fh.read()

PACKAGES = (
    'siginfo',
)

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Unix',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Software Development :: Bug Tracking',
    'Topic :: Software Development :: Debuggers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: System :: Logging',
    'Topic :: System :: Monitoring'
]


setuptools.setup(
    name='siginfo',
    version=siginfo.__version__,
    author=siginfo.__author__,
    author_email="jonas.marcello@esbme.com",
    description="A Python package to help debugging and monitoring python script",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/anergictcell/siginfo",
    license='MIT',
    packages=PACKAGES,
    classifiers=CLASSIFIERS,
    python_requires='>=2.7',
    include_package_data=True
)
