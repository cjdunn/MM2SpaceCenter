'''build RoboFont Extension'''

import os
from mojo.extensions import ExtensionBundle

# get current folder
basePath = os.path.dirname(__file__)

# source folder for all extension files
sourcePath = os.path.join(basePath, 'source')

# folder with python files
libPath = os.path.join(sourcePath, 'lib')

# folder with html files
htmlPath = os.path.join(sourcePath, 'html')

# folder with resources (icons etc)
resourcesPath = os.path.join(sourcePath, 'resources')

# load license text from file
# see choosealicense.com for more open-source licenses
licensePath = os.path.join(basePath, 'source/LICENSE.txt')

# boolean indicating if only .pyc should be included
pycOnly = ["3.6", "3.7"]

# name of the compiled extension file
extensionFile = 'MM2SpaceCenter.roboFontExt'

# path of the compiled extension
buildPath = basePath
extensionPath = os.path.join(buildPath, extensionFile)

# initiate the extension builder
B = ExtensionBundle()

# name of the extension
B.name = "MM2SpaceCenter"

# name of the developer
B.developer = 'CJType'

# URL of the developer
B.developerURL = 'http://github.com/cjdunn'

# extension icon (file path or NSImage)
imagePath = os.path.join(resourcesPath, 'html/MM2SpaceCenterMechanicIcon.png')
B.icon = imagePath

# version of the extension
B.version = '0.1.3'

# should the extension be launched at start-up?
B.launchAtStartUp = True

# script to be executed when RF starts
B.mainScript = 'MM2SpaceCenter.py'

# does the extension contain html help files?
B.html = True

# minimum RoboFont version required for this extension
B.requiresVersionMajor = '3'
B.requiresVersionMinor = '3'

# scripts which should appear in Extensions menu
B.addToMenu = [
    {
        'path' : 'MM2SpaceCenter.py',
        'preferredName': 'MM2SpaceCenter',
        'shortKey' : '',
    },

]

# license for the extension
with open(licensePath) as license:
    B.license = license.read()

# expiration date for trial extensions
B.expireDate = '2021-03-31'

# compile and save the extension bundle
print('building extension...', end=' ')
B.save(extensionPath, libPath=libPath, htmlPath=htmlPath, resourcesPath=resourcesPath, pycOnly=pycOnly)
print('done!')

# check for problems in the compiled extension
print()
print(B.validationErrors())