from setuptools import setup, find_packages

setup(
    name='smugify',
    version='0.1.0',
    author='Vu2n',
    description='One-import utility library for Python: logs, alerts, APIs, CLI, all smug.',
    long_description = "smugify: because why should you try harder?",
    long_description_content_type = "text/plain",
    url='https://github.com/Vu2n/smugify',
    packages=find_packages(),
    install_requires=[
        'requests',
        'win10toast; platform_system=="Windows"'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
