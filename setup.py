from setuptools import setup, find_packages


description = (
    'Sphinx extension for Data Dictionary and Database Diagram'
)

with open('README.rst', 'r', encoding='utf8') as f:
    long_description = f.read()

requires = [
    'Sphinx>=0.6',
    'PyYAML >= 3.12',
    'jsonschema >= 2.5.1',
    'recommonmark >= 0.4.0',
]

keywords = [
    'sphinx',
    'sphinxcontrib',
    'data dictionary',
    'database diagram',
]

setup(
    name='sphinxcontrib-dd',
    version='0.1.3',
    url='https://github.com/julot/sphinxcontrib-dd',
    license='MIT',
    author='Andy Yulius',
    author_email='julot@gmail.com',
    description=description,
    long_description=long_description,
    keywords=' '.join(keywords),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
