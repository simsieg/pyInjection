from setuptools import setup, find_packages


setup(
    name="pyInjection",
    version="0.1.3",
    author="James Brown",
    author_email="jbrown@uber.com",
    url="https://github.com/simsieg/pyInjection",
    description="simple python ast consumer which searches for common SQL injection attacks",
    license='MIT (Expat)',
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Security",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(exclude=["tests"]),
    entry_points={
        "console_scripts": [
            "pyInjection = pyInjection:main",
        ]
    },
    tests_require=["nose==1.3.0", "mock==1.0.1"],
    test_suite="nose.collector",
    long_description="pyInjection"

Walks the AST and looks for arguments to cursor.execute or session.execute; then
determines whether string interpolation, concatenation or the .format() call is used
on those arguments. Not at all comprehensive, but better than nothing.
"""
)
