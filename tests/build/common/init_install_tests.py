"""
Test for init and install command

Specs:

Init command should init package.json
Install command should install all listed dependencies (npm install)
"""
import fileinput
import os

from core.base_class.BaseClass import BaseClass
from core.npm.npm import Npm
from core.osutils.command import run
from core.osutils.file import File
from core.osutils.folder import Folder
from core.settings.settings import TNS_PATH, CURRENT_OS, OSType, TEST_RUN_HOME, SUT_FOLDER
from core.settings.strings import *
from core.tns.tns import Tns
from core.tns.tns_verifications import TnsAsserts


class InitAndInstallTests(BaseClass):
    @classmethod
    def setUpClass(cls):
        BaseClass.setUpClass(cls.__name__)

    def setUp(self):
        BaseClass.setUp(self)
        Folder.cleanup(self.app_name)

    def tearDown(self):
        BaseClass.tearDown(self)
        Folder.cleanup(self.app_name)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_201_init_defaults(self):
        Folder.cleanup(BaseClass.app_name)
        Folder.create(BaseClass.app_name)
        Folder.navigate_to(BaseClass.app_name)
        output = Tns.init(attributes={"--force": ""}, tns_path=os.path.join("..", TNS_PATH), assert_success=False)
        Folder.navigate_to(TEST_RUN_HOME, relative_from_current_folder=False)
        assert successfully_initialized in output

        assert File.exists(self.app_name + "/package.json")
        assert not File.exists(self.app_name + "/app")
        assert not File.exists(self.app_name + "/platform")

        output = File.read(self.app_name + "/package.json")
        assert app_identifier in output.lower()
        assert "tns-android" in output
        assert tns_core_modules in output
        if CURRENT_OS == OSType.OSX:
            assert "tns-ios" in output

    def test_202_init_path(self):
        Tns.init(attributes={"--path": self.app_name, "--force": ""})
        assert File.exists(self.app_name + "/package.json")
        assert not File.exists(self.app_name + "/app")
        assert not File.exists(self.app_name + "/platform")

        output = File.read(self.app_name + "/package.json")
        assert app_identifier in output.lower()
        assert "tns-android" in output
        if CURRENT_OS == OSType.OSX:
            assert "tns-ios" in output

    def test_203_init_update_existing_file(self):
        self.test_202_init_path()
        # Modify existing file
        for line in fileinput.input(self.app_name + "/package.json", inplace=1):
            print line.lower().replace(app_identifier, "org.nativescript.TestApp12"),
        output = File.read(self.app_name + "/package.json")
        print output
        assert "org.nativescript.TestApp12" in output

        # Overwrite changes
        self.test_202_init_path()

    def test_204_install_defaults(self):
        self.test_202_init_path()
        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/platforms/android/build.gradle")

        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TestApp.xcodeproj")

    def test_205_install_node_modules(self):
        self.test_202_init_path()

        Npm.install(package="gulp", option="--save-dev", folder=BaseClass.app_name)
        Npm.install(package="lodash", option="--save", folder=BaseClass.app_name)

        output = File.read(self.app_name + "/package.json")
        assert devDependencies in output
        assert "gulp" in output
        assert "lodash" in output

        Folder.cleanup(self.app_name + '/platforms')
        assert not File.exists(self.app_name + "/platforms")
        Folder.cleanup(self.app_name + '/node_modules')
        assert not File.exists(self.app_name + "/node_modules")

        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/node_modules/lodash")
        assert File.exists(self.app_name + "/node_modules/gulp")

        assert File.exists(self.app_name + "/platforms/android/build.gradle")

        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TestApp.xcodeproj")

    def test_300_install_node_modules_if_node_modules_folder_exists(self):
        self.test_202_init_path()

        Npm.install(package="gulp", option="--save-dev", folder=BaseClass.app_name)
        Npm.install(package="lodash", option="--save", folder=BaseClass.app_name)

        output = File.read(self.app_name + "/package.json")
        assert devDependencies in output
        assert "gulp" in output
        assert "lodash" in output

        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/node_modules/lodash")
        assert File.exists(self.app_name + "/node_modules/gulp")
        assert File.exists(self.app_name + "/platforms/android/build.gradle")
        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TestApp.xcodeproj")

    def test_301_install_and_prepare(self):
        self.test_202_init_path()
        Tns.platform_add_android(attributes={"--path": self.app_name}, version="next")

        Npm.install(package='', folder=BaseClass.app_name)
        Npm.install(package="gulp", option="--save-dev", folder=BaseClass.app_name)
        Npm.install(package="lodash", option="--save", folder=BaseClass.app_name)

        source = os.path.join(SUT_FOLDER, "template-hello-world", "app")
        dest = os.path.join(self.app_name, "app")
        Folder.copy(source, dest)

        output = File.read(self.app_name + "/package.json")
        assert devDependencies in output
        assert "gulp" in output
        assert "lodash" in output

        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/node_modules/lodash")
        assert File.exists(self.app_name + "/node_modules/gulp")
        assert File.exists(self.app_name + "/platforms/android/build.gradle")

        Tns.prepare_android(attributes={"--path": self.app_name})
        assert File.exists(os.path.join(self.app_name, TnsAsserts.PLATFORM_ANDROID_NPM_MODULES_PATH, "lodash"))
        assert not File.exists(os.path.join(self.app_name, TnsAsserts.PLATFORM_ANDROID_NPM_MODULES_PATH, "gulp"))

        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TestApp.xcodeproj")
            Tns.prepare_ios(attributes={"--path": self.app_name})
            assert File.exists(os.path.join(self.app_name, TnsAsserts.PLATFORM_ANDROID_NPM_MODULES_PATH, "lodash"))
            assert not File.exists(os.path.join(self.app_name, TnsAsserts.PLATFORM_ANDROID_NPM_MODULES_PATH, "gulp"))

    def test_400_install_in_not_existing_folder(self):
        output = Tns.install(attributes={"--path": self.app_name}, assert_success=False)
        assert "No project found" in output
