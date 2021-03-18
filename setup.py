from setuptools import setup

setup(
    name="Flask-CacheBuster",
    version="1.0.0",
    description="Flask-CacheBuster is a lightweight Flask extension that adds a hash to the URL query parameters of each static file.",
    packages=["flask_cachebuster"],
    license="MIT",
    url="https://github.com/israel-fl/Flask-CacheBust",
    install_requires=[
        "Flask",
    ],
)
