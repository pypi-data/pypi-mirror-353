from setuptools import setup, find_packages

setup(
    name='smartio',
    version='0.1.0',
    description='Unified interactive print and input for console, Tkinter, and web.',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'flask',    # your web dependency
        # tkinter is part of stdlib, so no need to list
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
)
