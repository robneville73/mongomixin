
from setuptools import setup

requires = ['pymongo','deform','mongoengine','colander']

setup(name='mongomixin',
    version='0.0',
    description='mongomixin',
    classifiers=[
        "Programming Language :: Python",
    ],
    author="Rob Neville",
    author_email='robertneville73@gmail.com',
    url="https://github.com/robneville73/mongomixin",
    keywords="web pyramid python pylons mongodb mongoengine colander deform",
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
)