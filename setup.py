from setuptools import setup

setup(
    name="selenium-trio",
    version="0.0.3",
    author="Ross Rochford",
    packages=[
        'selenium_trio', 
        'selenium_trio.extras', 
        'selenium_trio.extras.async_property',
        'selenium_trio.extras.javascript',
    ],
    dependeny_links=[],
    classifiers=[],
)
