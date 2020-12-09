import setuptools

#README.md auslesen und als description verwenden
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# zwingende Abhaengigkeiten
# Hier einfach den Inhalt vom requirements einfuegen.
# wohl ohne das Ganze Anaconda zeuggs am Schluss.
# Ich wuerde auch ohne fixe Versions angabe.
deps = []


# Optionale Abhaengigkeiten
# Installieren mit pip install MODULENAME['full']
# Hier koennte man auch die moeglichkeit bieten, eine Version zu machen
# fuer entwickler und eine fuer user. Also full mit allen Test Modulen
# und eine User Version mit nur dem noetigsten zum starten...
optional_deps = {
        "full": ['wheel', 'setuptools', 'pytest', 'pytest-html', 'keyring', 'twine'],
        "minimal": []
        }


setuptools.setup(
    name='HitachiBlockAPI',
    packages=['HitachiBlockAPI'],
    version='0.9.2',
    author="Pascal Hubacher",
    description='Hitachi Storage REST API to ease the communication to Hitachi Storage',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/pascalhubacher/HitachiStorageRestAPI',
    install_requires=deps,
    extras_require=optional_deps,
    scripts=[]
)