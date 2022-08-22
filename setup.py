from distutils.core import setup

setup(
    name="aprs2influxdb",
    version="0.2.1",
    author="Bryce Salmi",
    author_email="Bryce@FaradayRF.com",
    packages=["aprs2influxdb"],
    url="https://github.com/FaradayRF/aprs2influxdb",
    license="GPLv3",
    description="Interfaces ham radio APRS-IS servers and saves packet data into an influxdb database",
    long_description=open("README.md").read(),
    install_requires=[
        "aprslib==0.7.2",
        "influxdb==5.3.1"
    ],
    entry_points={
        "console_scripts":
            ["aprs2influxdb = aprs2influxdb.main:main"]
    }
)
