import os
import time

from helpers._os_lib import KillProcess, runAUT


def StartEmulator(name="Nexus4"):
    
    StopEmulators()
    
    print os.name
    
    if 'nt' in os.name:
        runAUT("emulator -avd Nexus4 -no-skin -no-audio -no-window", None, False)
    else:                      
        runAUT("emulator -avd Nexus4 -no-skin -no-audio -no-window &", None, False)

def WaitForEmulator():

    for counter in range(1, 5):
        time.sleep(10)
        output = runAUT("adb devices");
        print output
        if "emulator-5554device" in output.replace(" ", ""):
            break

def StopEmulators():
    KillProcess("emulator")
