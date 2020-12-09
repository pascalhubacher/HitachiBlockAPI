import setuptools

# Read infos from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# mandatory depencies
deps = []

# optional depencies for "maintainer"
optional_deps = {
        "full": ['wheel', 'setuptools', 'pytest', 'pytest-html', 'keyring', 'twine'],
        "minimal": []
        }

setuptools.setup(
    name='HitachiBlockAPI',
    packages=['HitachiBlockAPI'],
    version='0.9.3',
    author="Pascal Hubacher",
    description='Python Class for Hitachi Storage REST API to ease the communication to Hitachi Storage',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/pascalhubacher/HitachiBlockAPI',
    install_requires=deps,
    extras_require=optional_deps,
    scripts=[]
)