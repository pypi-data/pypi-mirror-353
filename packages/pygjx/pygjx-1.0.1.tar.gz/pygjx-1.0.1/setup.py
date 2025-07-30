from setuptools import setup, find_packages
import sys
if not sys.platform.startswith("win"):raise OSError("This package can only be installed on Windows.")
setup(name="pygjx",version="1.0.1",packages=find_packages(),description="pygjx",long_description=open("README.md").read(),author="Zeng Yuye",platforms=["Windows"],url="https://github.com/Azyy629/A-",author_email="341212429@qq.com",phone="+8613538790701",install_requires=["speedtest-cli","tqdm","requests","opencv-python","pygame","pyautogui","pyinstaller","pip","pywin32"],classifiers=["Programming Language :: Python :: 3","License :: OSI Approved :: MIT License","Operating System :: Microsoft :: Windows",])
print("""Instructions for use of pygjx v1.0.1 module:
Download http link:dhttp(url)
Computer shutdown:gj()
Computer hibernation:xm()
Computer restart: cq()
Computer sleep:sm()
Test the computer network speed (some countries/regions may have errors):cws() # Return to the list type, the first item is the download speed, and the second item is the upload speed.""")
