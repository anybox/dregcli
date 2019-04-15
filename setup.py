from setuptools import setup, find_packages


def parse_requirements(file):
    required = []
    with open(file) as f:
        for req in f.read().splitlines():
            if not req.strip().startswith('#'):
                required.append(req)
    return required


version = '0.1a0'
requires = parse_requirements('requirements.txt')
tests_requires = parse_requirements('requirements.tests.txt')

setup(
    name='dregcli',
    version=version,
    description="Docker registry API v2 client, and console tool",
    long_description="""
    This is a command line utility tool for docker registry API v2
    """,
    classifiers=[
        'Development Status :: 3 - Alpha  ',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
    ],
    author='Vincent GREINER',
    author_email='vgreiner@anybox.fr',
    url='https://github.com/anybox/dregcli',
    license='MIT',
    packages=find_packages(
        exclude=['ez_setup', 'examples', 'tests']
    ),
    include_package_data=True,
    zip_safe=False,
    namespace_packages=['dregcli'],
    install_requires=requires,
    tests_require=requires + tests_requires,
    entry_points="""
    [console_scripts]
    dregcli=dregcli.console:main
    """,
)
