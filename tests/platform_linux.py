'''
Test platform add (android)
'''
import os
import platform
from time import sleep
import unittest

from helpers._os_lib import run_aut, cleanup_folder, is_empty, \
    check_file_exists
from helpers._tns_lib import ANDROID_RUNTIME_PATH, ANDROID_RUNTIME_SYMLINK_PATH, build, \
    TNS_PATH, create_project, create_project_add_platform, platform_add


# C0103 - Invalid %s name "%s"
# C0111 - Missing docstring
# R0201 - Method could be a function
# R0904 - Too many public methods
# pylint: disable=C0103, C0111, R0201, R0904
class PlatformAndroid(unittest.TestCase):

    def setUp(self):

        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""

        cleanup_folder('./TNS_App')

    def tearDown(self):
        pass

    def test_001_platform_list_empty_project(self):
        create_project(proj_name="TNS_App")
        output = run_aut(TNS_PATH + " platform list --path TNS_App")

        assert "No installed platforms found. Use $ tns platform add" in output
        if 'Darwin' in platform.platform():
            assert "Available platforms for this OS:  ios and android" in output
        else:
            assert "Available platforms for this OS:  android" in output

    def test_002_platform_add_android(self):
        create_project(proj_name="TNS_App")
        output = platform_add(platform="android", path="TNS_App")
        assert "Copying template files..." in output
        assert "Project successfully created" in output

        if ('TEST_RUN' in os.environ) and (not "SMOKE" in os.environ[
                'TEST_RUN']) and ("2" in os.environ['ANDROID_HOME']):
            assert check_file_exists(
                'TNS_App/platforms/android',
                'platform_android_1.3.0.txt')

    def test_003_platform_add_android_framework_path(self):
        create_project(proj_name="TNS_App")
        output = platform_add(
            platform="android",
            framework_path=ANDROID_RUNTIME_PATH,
            path="TNS_App")
        assert "Copying template files..." in output
        assert "Project successfully created" in output

        if ('TEST_RUN' in os.environ) and (not "SMOKE" in os.environ[
                'TEST_RUN']) and ("2" in os.environ['ANDROID_HOME']):
            assert check_file_exists(
                'TNS_App/platforms/android',
                'platform_android_current.txt')

    @unittest.skip(
        "This test is not valid, adding symlink platform from npm cache cause issues")
    def test_004_platform_add_android_symlink(self):
        if 'Windows' in platform.platform():
            print "Ignore because of https://github.com/NativeScript/nativescript-cli/issues/282"
        else:
            create_project(proj_name="TNS_App")
            output = platform_add(
                platform="android",
                path="TNS_App",
                symlink=True)
            assert "Copying template files..." in output
            assert "Project successfully created" in output

            if ('TEST_RUN' in os.environ) and (not "SMOKE" in os.environ[
                    'TEST_RUN']) and ("2" in os.environ['ANDROID_HOME']):
                assert check_file_exists(
                    'TNS_App/platforms/android',
                    'platform_android_symlink.txt')

    def test_005_platform_add_android_symlink_and_frameworkPath(self):
        if 'Windows' in platform.platform():
            print "Ignore because of https://github.com/NativeScript/nativescript-cli/issues/282"
        else:
            create_project(proj_name="TNS_App")
            output = platform_add(
                platform="android",
                path="TNS_App",
                framework_path=ANDROID_RUNTIME_SYMLINK_PATH,
                symlink=True)
            assert "Copying template files..." in output
            assert "Project successfully created" in output

            if ('TEST_RUN' in os.environ) and (not "SMOKE" in os.environ[
                    'TEST_RUN']) and ("2" in os.environ['ANDROID_HOME']):
                assert check_file_exists(
                    'TNS_App/platforms/android',
                    'platform_android_symlink.txt')

    def test_200_platform_list_inside_empty_project(self):
        create_project(proj_name="TNS_App")
        current_dir = os.getcwd()
        os.chdir(os.path.join(current_dir, "TNS_App"))
        output = run_aut(os.path.join("..", TNS_PATH) + " platform list")
        os.chdir(current_dir)

        assert "No installed platforms found. Use $ tns platform add" in output
        if 'Darwin' in platform.platform():
            assert "Available platforms for this OS:  ios and android" in output
        else:
            assert "Available platforms for this OS:  android" in output

    def test_201_platform_add_android_inside_project(self):
        create_project(proj_name="TNS_App")
        current_dir = os.getcwd()
        os.chdir(os.path.join(current_dir, "TNS_App"))
        output = run_aut(os.path.join("..", TNS_PATH) + " platform add android")
        os.chdir(current_dir)

        assert "Copying template files..." in output
        assert "Project successfully created" in output

        if ('TEST_RUN' in os.environ) and (not "SMOKE" in os.environ[
                'TEST_RUN']) and ("2" in os.environ['ANDROID_HOME']):
            assert check_file_exists(
                'TNS_App/platforms/android',
                'platform_android_1.3.0.txt')

    def test_202_platform_remove_android(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="android",
            framework_path=ANDROID_RUNTIME_PATH)

        output = run_aut(TNS_PATH + " platform remove android --path TNS_App")
        assert "Platform android successfully removed." in output

        assert not "error" in output
        assert is_empty('TNS_App/platforms')

        output = run_aut("cat TNS_App/package.json")
        assert not "tns-android" in output

    def test_203_platform_add_android_custom_version(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="android@1.3.0")
        output = run_aut("cat TNS_App/package.json")
        assert "\"version\": \"1.3.0\"" in output

        if ('TEST_RUN' in os.environ) and (not "SMOKE" in os.environ[
                'TEST_RUN']) and ("2" in os.environ['ANDROID_HOME']):
            assert check_file_exists(
                'TNS_App/platforms/android',
                'platform_android_1.3.0.txt')

    @unittest.skip("1.3.0 do not support older versions, enable after 1.3.1 is released")
    def test_204_platform_update_android(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="android@1.1.0")
        output = run_aut("cat TNS_App/package.json")
        assert "\"version\": \"1.1.0\"" in output

        command = TNS_PATH + " platform update android@1.2.0 --path TNS_App"
        output = run_aut(command)
        assert "Successfully updated to version  1.2.0" in output

        output = run_aut("cat TNS_App/package.json")
        assert "\"version\": \"1.2.0\"" in output

        if ('TEST_RUN' in os.environ) and (not "SMOKE" in os.environ[
                'TEST_RUN']) and ("2" in os.environ['ANDROID_HOME']):
            assert check_file_exists(
                'TNS_App/platforms/android',
                'platform_android_1.2.0.txt')
        build(platform="android", path="TNS_App")

    def test_205_platform_update_android_to_same_version(self):
        create_project_add_platform(proj_name="TNS_App", platform="android")
        output = run_aut(TNS_PATH + " platform update android --path TNS_App")
        assert "Current and new version are the same." in output
        assert "Usage" in output
        build(platform="android", path="TNS_App")

    @unittest.skip("1.3.0 do not support older versions, enable after 1.3.1 is released")
    def test_206_platform_downgrade_android_to_old_version(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="android@1.2.0")
        output = run_aut("cat TNS_App/package.json")
        assert "\"version\": \"1.2.0\"" in output

#         Comment these lines as they cause the test to fail
#         since commits in master on July 27, 2015
#         [31;1mCannot read property 'substring' of undefined[0m
#         TypeError: Cannot read property 'substring' of undefined

#         command = TNS_PATH + " platform update android@1.1.0 --path TNS_App"
#         output = run_aut(command + " < y_key.txt")
#         assert "You are going to downgrade to android runtime v.1.1.0. Are you sure?" in output
#         assert "Successfully updated to version  1.1.0" in output

        os.system(
            TNS_PATH +
            " platform update android@1.1.0 --path TNS_App < y_key.txt")
        sleep(10)

        output = run_aut("cat TNS_App/package.json")
        assert "\"version\": \"1.1.0\"" in output
        build(platform="android", path="TNS_App")

    @unittest.skip(
        "Execute when platform update command starts respecting --frameworkPath.")
    def test_207_platform_update_android_to_latest_version(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="android@1.0.0")
        output = run_aut("cat TNS_App/package.json")
        assert "\"version\": \"1.0.0\"" in output

        command = TNS_PATH + \
            " platform update android --frameworkPath {0} --path TNS_App".format(
                ANDROID_RUNTIME_PATH)
        output = run_aut(command)
        assert "Successfully updated to version" in output
        build(platform="android", path="TNS_App")

    @unittest.skip(
        "Skiped because of https://github.com/NativeScript/nativescript-cli/issues/784")
    def test_208_platform_downgrade_android_from_latest_version(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="android",
            framework_path=ANDROID_RUNTIME_PATH)

        output = run_aut("cat TNS_App/package.json")
        assert "\"version\": \"1." in output

#         Comment these lines as they cause the test to fail
#         since commits in master on July 27, 2015
#         [31;1mCannot read property 'substring' of undefined[0m
#         TypeError: Cannot read property 'substring' of undefined

#         command = TNS_PATH + " platform update android@1.0.0 --path TNS_App"
#         output = run_aut(command + " < y_key.txt")
#         assert "You are going to downgrade to android runtime v.1.0.0. Are you sure?" in output
#         assert "Successfully updated to version  1.0.0" in output

        os.system(
            TNS_PATH +
            " platform update android@1.1.0 --path TNS_App < y_key.txt")
        sleep(10)

        output = run_aut("cat TNS_App/package.json")
        assert "\"version\": \"1.1.0\"" in output
        build(platform="android", path="TNS_App")

    def test_210_platform_update_android_patform_not_added(self):
        create_project(proj_name="TNS_App")
        output = run_aut(TNS_PATH + " platform update android --path TNS_App")
        assert "Copying template files..." in output
        assert "Project successfully created." in output
        assert not is_empty(
            "TNS_App/platforms/android/build-tools/android-static-binding-generator")

    def test_220_set_sdk(self):
        create_project(proj_name="TNS_App")
        platform_add(
            platform="android --sdk 19",
            framework_path=ANDROID_RUNTIME_PATH,
            path="TNS_App")

        output = run_aut(
            "cat TNS_App/platforms/android/src/main/AndroidManifest.xml ")
        assert "android:minSdkVersion=\"17\"" in output
        assert "android:targetSdkVersion=\"19\"" in output

    def test_221_set_sdk_not_installed(self):
        create_project(proj_name="TNS_App")
        output = platform_add(
            platform="android --sdk 29",
            framework_path=ANDROID_RUNTIME_PATH,
            path="TNS_App")
        assert "Support for the selected Android target SDK android-29 is not verified. " + \
        "Your Android app might not work as expected." in output

        output = run_aut(
            "cat TNS_App/platforms/android/src/main/AndroidManifest.xml")
        assert "android:minSdkVersion=\"17\"" in output
        assert "android:targetSdkVersion=\"29\"/>" in output

    def test_400_platform_list_wrong_path(self):
        output = run_aut(TNS_PATH + " platform list")
        assert "No project found at or above" in output
        assert "and neither was a --path specified." in output

    def test_401_platform_list_wrong_path(self):
        output = run_aut(TNS_PATH + " platform list --path invalidPath")
        assert "No project found at or above" in output
        assert "and neither was a --path specified." in output

    def test_420_platform_add_existing_platform(self):
        self.test_002_platform_add_android()

        output = run_aut(TNS_PATH + " platform add android --path TNS_App")
        assert "Platform android already added" in output

    def test_421_platform_add_android_wrong_framework_path(self):
        create_project(proj_name="TNS_App")
        output = run_aut(
            TNS_PATH +
            " platform add android --frameworkPath invalidFile.tgz --path TNS_App")
        assert "Error: no such package available" in output
        assert "invalidFile.tgz" in output

    def test_423_platform_add_android_wrong_framework_path_option(self):
        create_project(proj_name="TNS_App")
        output = run_aut(
            TNS_PATH +
            " platform add android --frameworkpath tns-android.tgz --path TNS_App")
        assert "The option 'frameworkpath' is not supported." in output

    def test_424_platform_add_android_wrong_symlink_option(self):
        create_project(proj_name="TNS_App")
        output = run_aut(
            TNS_PATH +
            " platform add android --frameworkPath tns-android.tgz --simlink --path TNS_App")
        assert "The option 'simlink' is not supported." in output

    def test_425_platform_add_empty_platform(self):
        create_project(proj_name="TNS_App")
        output = run_aut(TNS_PATH + " platform add --path TNS_App")
        assert "No platform specified. Please specify a platform to add" in output
        assert "Usage" in output

    def test_430_platform_remove_missing_platform(self):
        create_project(proj_name="TNS_App")
        output = run_aut(TNS_PATH + " platform remove android --path TNS_App")
        assert "The platform android is not added to this project. " + \
            "Please use 'tns platform add <platform>'" in output
        assert "Usage" in output

    def test_431_platform_remove_invalid_platform(self):
        create_project(proj_name="TNS_App")
        output = run_aut(
            TNS_PATH +
            " platform remove invalidPlatform --path TNS_App")
        assert "Invalid platform invalidplatform. Valid platforms are ios or android." in output
        assert "Usage" in output

    def test_432_platform_remove_empty_platform(self):
        create_project(proj_name="TNS_App")
        output = run_aut(TNS_PATH + " platform remove --path TNS_App")
        assert "No platform specified. Please specify a platform to remove" in output
        assert "Usage" in output

    def test_441_platform_update_invalid_platform(self):
        create_project(proj_name="TNS_App")
        output = run_aut(
            TNS_PATH +
            " platform update invalidPlatform --path TNS_App")
        assert "Invalid platform invalidplatform. Valid platforms are ios or android." in output
        assert "Usage" in output

    def test_442_platform_update_empty_platform(self):
        create_project(proj_name="TNS_App")
        output = run_aut(TNS_PATH + " platform update --path TNS_App")
        assert "1mNo platform specified. Please specify platforms to update" in output
        assert "Usage" in output
