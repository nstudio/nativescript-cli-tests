import os
import unittest

from helpers._os_lib import CleanupFolder, CheckOutput, runAUT, FileExists
from helpers._tns_lib import tnsPath, CreateProject, CreateProjectAndAddPlatform, \
    androidRuntimePath, Prepare, androidKeyStorePath, androidKeyStorePassword, \
    androidKeyStoreAlias, androidKeyStoreAliasPassword, PlatformAdd, \
    androidRuntimeSymlinkPath


class Build_Linux(unittest.TestCase):
    
    def setUp(self):
        
        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""
        
        CleanupFolder('./TNS_App');

    def tearDown(self):        
        pass

    def test_010_Build_Android_WithPrepare(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="android", frameworkPath=androidRuntimePath)     
        Prepare(path="TNS_App", platform="android") 
        output = runAUT(tnsPath + " build android --path TNS_App")
        
        # Even if project is already prepared build will prepare it again
        assert ("Project successfully prepared" in output) 
        assert ("Creating TNS_App-debug-unaligned.apk and signing it with a debug key..." in output)  
        assert ("BUILD SUCCESSFUL" in output)
        assert ("Project successfully built" in output)         
        assert FileExists("TNS_App/platforms/android/bin/TNS_App-debug.apk")
                
    def test_011_Build_Android_WithOutPrepare(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="android", frameworkPath=androidRuntimePath)     
        output = runAUT(tnsPath + " build android --path TNS_App")
        
        # In 0.9.0 and above Build command automatically prepare project before build
        assert ("Project successfully prepared" in output) 
        assert ("Creating TNS_App-debug-unaligned.apk and signing it with a debug key..." in output)  
        assert ("BUILD SUCCESSFUL" in output)
        assert ("Project successfully built" in output)        
        assert FileExists("TNS_App/platforms/android/bin/TNS_App-debug.apk")
                    
    def test_012_Build_Android_InsideProject(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="android", frameworkPath=androidRuntimePath)     
        currentDir = os.getcwd()   
        os.chdir(os.path.join(currentDir,"TNS_App"))    
        output = runAUT(os.path.join("..", tnsPath) + " build android --path TNS_App")
        os.chdir(currentDir);
        assert ("Project successfully prepared" in output) 
        assert ("BUILD SUCCESSFUL" in output)
        assert ("Project successfully built" in output)   
        assert FileExists("TNS_App/platforms/android/bin/TNS_App-debug.apk")
        
    def test_013_Build_Android_Release(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="android", frameworkPath=androidRuntimePath)     
        output = runAUT(tnsPath + " build android --keyStorePath " + androidKeyStorePath + 
                        " --keyStorePassword " + androidKeyStorePassword + 
                        " --keyStoreAlias " + androidKeyStoreAlias + 
                        " --keyStoreAliasPassword " + androidKeyStoreAliasPassword + 
                        " --release --path TNS_App")
        assert ("Building Libraries with 'release'..." in output)
        assert ("Project successfully prepared" in output) 
        assert ("BUILD SUCCESSFUL" in output)
        assert ("Signing final apk..." in output)
        assert ("Project successfully built" in output)
        assert FileExists("TNS_App/platforms/android/bin/TNS_App-release.apk")
        
    # Note: This test fails only on Windows.
    # TODO: Ignore tests at runtime (in tns_tests_runner.py). This will allow test to be ignored only on specific OS
    @unittest.skip("Skipped because of https://github.com/NativeScript/nativescript-cli/issues/282")         
    def test_014_Build_SymlinkProject(self):
        CreateProject(projName="TNS_App")
        output = PlatformAdd(platform="android", path="TNS_App", frameworkPath=androidRuntimeSymlinkPath, symlink=True)
        assert("Project successfully created" in output)
        output = runAUT(tnsPath + " build android --path TNS_App")
        assert ("Project successfully prepared" in output) 
        assert ("BUILD SUCCESSFUL" in output)
        assert ("Project successfully built" in output)  
               
    def test_400_Build_MissingPlatform(self):
        output = runAUT(tnsPath + " build")
        assert CheckOutput(output, 'build_help_output.txt')
    
    def test_401_Build_InvalidPlatform(self):
        output = runAUT(tnsPath + " build invalidCommand")
        assert ("The input is not valid sub-command for 'build' command" in output)
        assert CheckOutput(output, 'build_help_output.txt')
        
    def test_402_Build_Android_WithOutPath(self):
        output = runAUT(tnsPath + " build android")
        assert ("No project found at or above" in output)
        assert ("and neither was a --path specified." in output)
        assert CheckOutput(output, 'buildandroid_help_output.txt')
        
    def test_403_Build_Android_WithOutPath(self):
        output = runAUT(tnsPath + " build android --path invalidPath")
        assert ("No project found at or above" in output)
        assert ("and neither was a --path specified." in output)
        assert CheckOutput(output, 'buildandroid_help_output.txt')

    @unittest.skip("Skipped because of https://github.com/NativeScript/nativescript-cli/issues/277")             
    def test_404_Build_Android_WhenPlatformIsNotAdded(self):
        CreateProject(projName="TNS_App")
        output = runAUT(tnsPath + " build android --path TNS_App")
        # TODO: Verify after issue is fixed
        assert not ("error" in output)

    @unittest.skip("Skipped because of https://github.com/NativeScript/nativescript-cli/issues/251")          
    def test_405_Build_Android_WithWrongParam(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="android", frameworkPath=androidRuntimePath)
        output = runAUT(tnsPath + " build android --invalidOption --path TNS_App")
        assert ("The option '--invalidOption' is not supported." in output)
        assert not ("error" in output)