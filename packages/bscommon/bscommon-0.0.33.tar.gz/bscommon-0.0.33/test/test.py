import os
import sys
scriptDir = os.path.dirname(__file__)+os.sep
rootDir=scriptDir+".."+os.sep
sys.path.append(rootDir)
from src.bscommon import Com
from src.bscommon import Ssh
sys.path.remove(rootDir)




Ssh.init(scriptDir)
Ssh.sshHostRun("setup",args={"bs9.top"})