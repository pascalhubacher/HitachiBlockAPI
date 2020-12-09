import setuptools


# zwingende Abhaengigkeiten
# Hier einfach den Inhalt vom requirements einfuegen.
# wohl ohne das Ganze Anaconda zeuggs am Schluss.
# Ich wuerde auch ohne fixe Versions angabe.
deps = []


# Optionale Abhaengigkeiten
# Installieren mit pip install MODULENAME[full']
# Hier koennte man auch die moeglichkeit bieten, eine Version zu machen
# fuer entwickler und eine fuer user. Also full mit allen Test Modulen
# und eine User Version mit nur dem noetigsten zum starten...
optional_deps = {
        "full": [],
        "minimal": []
        }


setuptools.setup(
    name='StorageRestAPI',
    packages=['StorageRestAPI'],
    version='0.9.8',
    description='Hitachi Storage REST API Project',
    url='https://github.com/pascalhubacher/HitachiStorageRestAPI',
    install_requires=deps,
    extras_require=optional_deps,
    scripts=[]
)