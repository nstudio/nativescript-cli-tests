"""
Test for `tns run android` command with different nsconfig setup.
Run should sync all the changes correctly:
 - Valid changes in CSS, JS, XML should be applied.
 - Invalid changes in XML should be logged in the console and lives-sync should continue when XML is fixed.
 - Hidden files should not be synced at all.
 - --syncAllFiles should sync changes in node_modules
 - --justlaunch should release the console.
If emulator is not started and device is not connected `tns run android` should start emulator.
"""

import os
from nose_parameterized import parameterized

from core.base_class.BaseClass import BaseClass
from core.device.device import Device
from core.device.emulator import Emulator
from core.osutils.file import File
from core.osutils.folder import Folder
from core.settings.settings import ANDROID_PACKAGE, ANDROID_KEYSTORE_PATH, ANDROID_KEYSTORE_PASS, \
    ANDROID_KEYSTORE_ALIAS, ANDROID_KEYSTORE_ALIAS_PASS, EMULATOR_ID, EMULATOR_NAME, TEST_RUN_HOME
from core.tns.replace_helper import ReplaceHelper
from core.tns.tns import Tns
from core.tns.tns_platform_type import Platform


class RunAndroidEmulatorTests(BaseClass):
    @classmethod
    def setUpClass(cls):
        BaseClass.setUpClass(cls.__name__)
        Tns.kill()
        Emulator.stop()
        Emulator.ensure_available()
        Device.uninstall_app(app_prefix="org.nativescript.", platform=Platform.ANDROID)

        base_src = os.path.join(os.getcwd(), 'data', 'nsconfig')

        # Initial create of all projects
        app_name_change_app_location = "ChangeAppLocation"
        Tns.create_app(app_name=app_name_change_app_location,
                       attributes={'--template': os.path.join('data', 'apps', 'livesync-hello-world.tgz')},
                       update_modules=True)

        # Rename the app in AndroidManifest.xml to reuse the images
        File.replace(
            os.path.join(app_name_change_app_location, 'app', 'App_Resources', 'Android', 'AndroidManifest.xml'),
            "@string/app_name", "TestApp")

        # Create the other projects using the initial setup but in different folder
        app_name_change_app_location_and_name = "ChangeAppLocationAndName"
        Folder.cleanup(app_name_change_app_location_and_name)
        Folder.copy(app_name_change_app_location, app_name_change_app_location_and_name)

        # Rename the app
        File.replace(
            os.path.join(app_name_change_app_location_and_name, 'package.json'),
            "org.nativescript.ChangeAppLocation", "org.nativescript." + app_name_change_app_location_and_name)
        File.replace(
            os.path.join(app_name_change_app_location_and_name, 'app', 'App_Resources', 'Android', 'app.gradle'),
            "__PACKAGE__", "org.nativescript." + app_name_change_app_location_and_name)

        app_name_change_app_res_location = "ChangeAppResLocation"
        Folder.cleanup(app_name_change_app_res_location)
        Folder.copy(app_name_change_app_location, app_name_change_app_res_location)

        # Rename the app
        File.replace(
            os.path.join(app_name_change_app_res_location, 'package.json'),
            "org.nativescript.ChangeAppLocation", "org.nativescript." + app_name_change_app_res_location)
        File.replace(
            os.path.join(app_name_change_app_res_location, 'app', 'App_Resources', 'Android', 'app.gradle'),
            "__PACKAGE__", "org.nativescript." + app_name_change_app_res_location)

        app_name_change_app_res_location_in_root = "ChangeAppResLocationInRoot"
        Folder.cleanup(app_name_change_app_res_location_in_root)
        Folder.copy(app_name_change_app_location, app_name_change_app_res_location_in_root)

        # Rename the app
        File.replace(
            os.path.join(app_name_change_app_res_location_in_root, 'package.json'),
            "org.nativescript.ChangeAppLocation", "org.nativescript." + app_name_change_app_res_location_in_root)
        File.replace(
            os.path.join(app_name_change_app_res_location_in_root, 'app', 'App_Resources', 'Android', 'app.gradle'),
            "__PACKAGE__", "org.nativescript." + app_name_change_app_res_location_in_root)

        app_name_rename_app = "RenameApp"
        Folder.cleanup(app_name_rename_app)
        Folder.copy(app_name_change_app_location, app_name_rename_app)

        # Rename the app
        File.replace(
            os.path.join(app_name_rename_app, 'package.json'),
            "org.nativescript.ChangeAppLocation", "org.nativescript." + app_name_rename_app)
        File.replace(
            os.path.join(app_name_rename_app, 'app', 'App_Resources', 'Android', 'app.gradle'),
            "__PACKAGE__", "org.nativescript." + app_name_rename_app)

        app_name_rename_app_res = "RenameAppRes"
        Folder.cleanup(app_name_rename_app_res)
        Folder.copy(app_name_change_app_location, app_name_rename_app_res)

        # Rename the app
        File.replace(
            os.path.join(app_name_rename_app_res, 'package.json'),
            "org.nativescript.ChangeAppLocation", "org.nativescript." + app_name_rename_app_res)
        File.replace(
            os.path.join(app_name_rename_app_res, 'app', 'App_Resources', 'Android', 'app.gradle'),
            "__PACKAGE__", "org.nativescript." + app_name_rename_app_res)

        # Change app/ location to be 'new_folder/app'
        proj_root = os.path.join(app_name_change_app_location)
        app_path = os.path.join(proj_root, 'app')

        File.copy(os.path.join(base_src, app_name_change_app_location, 'nsconfig.json', ), app_name_change_app_location)
        Folder.create(os.path.join(proj_root, "new_folder"))
        Folder.move(app_path, os.path.join(proj_root, 'new_folder'))
        Tns.platform_add_android(attributes={"--path": app_name_change_app_location,
                                             "--frameworkPath": ANDROID_PACKAGE})

        # Change app/ name and place to be 'my folder/my app'
        proj_root = os.path.join(app_name_change_app_location_and_name)
        app_path = os.path.join(proj_root, 'app')

        File.copy(os.path.join(base_src, app_name_change_app_location_and_name, 'nsconfig.json'),
                  app_name_change_app_location_and_name)
        Folder.create(os.path.join(proj_root, "my folder"))
        os.rename(app_path, os.path.join(proj_root, "my app"))
        Folder.move(os.path.join(proj_root, "my app"), os.path.join(proj_root, "my folder"))
        Tns.platform_add_android(attributes={"--path": app_name_change_app_location_and_name,
                                             "--frameworkPath": ANDROID_PACKAGE})

        # Change App_Resources/ location to be 'app/res/App_Resources'
        proj_root = os.path.join(app_name_change_app_res_location)
        app_path = os.path.join(proj_root, 'app')
        app_res_path = os.path.join(app_path, 'App_Resources')

        File.copy(os.path.join(base_src, app_name_change_app_res_location, 'nsconfig.json'),
                  app_name_change_app_res_location)
        Folder.create(os.path.join(app_path, 'res'))
        Folder.move(app_res_path, os.path.join(app_path, 'res'))
        Tns.platform_add_android(attributes={"--path": app_name_change_app_res_location,
                                             "--frameworkPath": ANDROID_PACKAGE})

        # Change App_Resources/ location to be in project root/App_Resources
        proj_root = os.path.join(app_name_change_app_res_location_in_root)
        app_path = os.path.join(proj_root, 'app')
        app_res_path = os.path.join(app_path, 'App_Resources')

        File.copy(os.path.join(base_src, app_name_change_app_res_location_in_root, 'nsconfig.json'),
                  app_name_change_app_res_location_in_root)
        Folder.move(app_res_path, proj_root)
        Tns.platform_add_android(attributes={"--path": app_name_change_app_res_location_in_root,
                                             "--frameworkPath": ANDROID_PACKAGE})

        # Change app/ to renamed_app/
        proj_root = os.path.join(app_name_rename_app)
        app_path = os.path.join(proj_root, 'app')

        File.copy(os.path.join(base_src, app_name_rename_app, 'nsconfig.json'), app_name_rename_app)
        os.rename(app_path, os.path.join(proj_root, 'renamed_app'))
        Tns.platform_add_android(attributes={"--path": app_name_rename_app, "--frameworkPath": ANDROID_PACKAGE})

        # Change App_Resources/ to My_App_Resources/
        proj_root = os.path.join(app_name_rename_app_res)
        app_path = os.path.join(proj_root, 'app')
        app_res_path = os.path.join(app_path, 'App_Resources')

        File.copy(os.path.join(base_src, app_name_rename_app_res, 'nsconfig.json'), app_name_rename_app_res)
        os.rename(app_res_path, os.path.join(app_path, 'My_App_Resources'))
        Tns.platform_add_android(attributes={"--path": app_name_rename_app_res, "--frameworkPath": ANDROID_PACKAGE})

    def setUp(self):
        BaseClass.setUp(self)

    def tearDown(self):
        Tns.kill()
        BaseClass.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        BaseClass.tearDownClass()

        Folder.cleanup("ChangeAppLocation")
        Folder.cleanup("ChangeAppLocationAndName")
        Folder.cleanup("ChangeAppResLocation")
        Folder.cleanup("ChangeAppResLocationInRoot")
        Folder.cleanup("RenameApp")
        Folder.cleanup("RenameAppRes")

    @parameterized.expand([
        ('ChangeAppLocation',
         ['new_folder/app/main-view-model.js', 'taps', 'clicks'],
         ['new_folder/app/main-page.xml', 'TAP', 'TEST'],
         ['new_folder/app/app.css', '42', '99'],
         os.path.join('ChangeAppLocation', 'new_folder', 'app', 'App_Resources', 'Android', 'AndroidManifest.xml')),
        ('ChangeAppLocationAndName',
         ['my folder/my app/main-view-model.js', 'taps', 'clicks'],
         ['my folder/my app/main-page.xml', 'TAP', 'TEST'],
         ['my folder/my app/app.css', '42', '99'],
         os.path.join('ChangeAppLocationAndName', 'my folder', 'my app', 'App_Resources', 'Android',
                      'AndroidManifest.xml')),
        ('ChangeAppResLocation',
         ReplaceHelper.CHANGE_JS,
         ReplaceHelper.CHANGE_XML,
         ReplaceHelper.CHANGE_CSS,
         os.path.join('ChangeAppResLocation', 'app', 'res', 'App_Resources', 'Android', 'AndroidManifest.xml')),
        ('ChangeAppResLocationInRoot',
         ReplaceHelper.CHANGE_JS,
         ReplaceHelper.CHANGE_XML,
         ReplaceHelper.CHANGE_CSS,
         os.path.join('ChangeAppResLocationInRoot', 'App_Resources', 'Android', 'AndroidManifest.xml')),
        ('RenameApp',
         ['renamed_app/main-view-model.js', 'taps', 'clicks'],
         ['renamed_app/main-page.xml', 'TAP', 'TEST'],
         ['renamed_app/app.css', '42', '99'],
         os.path.join('RenameApp', 'renamed_app', 'App_Resources', 'Android', 'AndroidManifest.xml')),
        ('RenameAppRes',
         ReplaceHelper.CHANGE_JS,
         ReplaceHelper.CHANGE_XML,
         ReplaceHelper.CHANGE_CSS,
         os.path.join('RenameAppRes', 'app', 'My_App_Resources', 'Android', 'AndroidManifest.xml'))
    ])
    def test_001_tns_run_android_js_css_xml_manifest(self, app_name, change_js, change_xml, change_css,
                                                     app_res_path):
        """Make valid changes in JS,CSS and XML"""

        # `tns run android` and wait until app is deployed
        log = Tns.run_android(attributes={'--path': app_name, '--device': EMULATOR_ID}, wait=False,
                              assert_success=False)
        strings = ['Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID,
                   'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=180, check_interval=10)

        # Verify app looks correct inside emulator
        Device.screen_match(device_name=EMULATOR_NAME, device_id=EMULATOR_ID,
                            expected_image='livesync-hello-world_home')

        # Change JS and wait until app is synced
        ReplaceHelper.replace(app_name, change_js, sleep=10)
        strings = ['Successfully transferred main-view-model.js', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)
        text_changed = Device.wait_for_text(device_id=EMULATOR_ID, text='42 clicks left', timeout=20)
        assert text_changed, 'Changes in JS file not applied (UI is not refreshed).'

        # Change XML and wait until app is synced
        ReplaceHelper.replace(app_name, change_xml, sleep=3)
        strings = ['Successfully transferred main-page.xml', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)
        text_changed = Device.wait_for_text(device_id=EMULATOR_ID, text='TEST')
        assert text_changed, 'Changes in XML file not applied (UI is not refreshed).'

        # Change CSS and wait until app is synced
        ReplaceHelper.replace(app_name, change_css, sleep=3)
        strings = ['Successfully transferred app.css', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Verify application looks correct
        Device.screen_match(device_name=EMULATOR_NAME, device_id=EMULATOR_ID,
                            expected_image='livesync-hello-world_js_css_xml')

        # Rollback all the changes
        ReplaceHelper.rollback(app_name, change_js, sleep=10)
        strings = ['Successfully transferred main-view-model.js', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)

        ReplaceHelper.rollback(app_name, change_css, sleep=3)
        strings = ['Successfully transferred app.css', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)

        ReplaceHelper.rollback(app_name, change_xml, sleep=3)
        strings = ['Successfully transferred main-page.xml', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings)

        # Verify app looks correct inside emulator
        Device.screen_match(device_name=EMULATOR_NAME, device_id=EMULATOR_ID,
                            expected_image='livesync-hello-world_home')

        # Changes in App_Resources should rebuild native project
        File.replace(app_res_path, '17', '19')
        strings = ['Preparing project', 'Building project', 'Gradle build', 'Successfully synced application']
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=60)

        # Verify app looks correct inside emulator
        Device.screen_match(device_name=EMULATOR_NAME, device_id=EMULATOR_ID,
                            expected_image='livesync-hello-world_home')

    @parameterized.expand([
        ('ChangeAppLocation',
         ['new_folder/app/main-view-model.js', 'taps', 'clicks'],
         ['new_folder/app/main-page.xml', 'TAP', 'TEST'],
         ['new_folder/app/app.css', '42', '99']),
        ('ChangeAppLocationAndName',
         ['my folder/my app/main-view-model.js', 'taps', 'clicks'],
         ['my folder/my app/main-page.xml', 'TAP', 'TEST'],
         ['my folder/my app/app.css', '42', '99']),
        ('ChangeAppResLocation',
         ReplaceHelper.CHANGE_JS,
         ReplaceHelper.CHANGE_XML,
         ReplaceHelper.CHANGE_CSS),
        ('ChangeAppResLocationInRoot',
         ReplaceHelper.CHANGE_JS,
         ReplaceHelper.CHANGE_XML,
         ReplaceHelper.CHANGE_CSS),
        ('RenameApp',
         ['renamed_app/main-view-model.js', 'taps', 'clicks'],
         ['renamed_app/main-page.xml', 'TAP', 'TEST'],
         ['renamed_app/app.css', '42', '99']),
        ('RenameAppRes',
         ReplaceHelper.CHANGE_JS,
         ReplaceHelper.CHANGE_XML,
         ReplaceHelper.CHANGE_CSS)
    ])
    def test_100_tns_run_android_release(self, app_name, change_js, change_xml, change_css):
        """Make valid changes in JS,CSS and HTML"""
        # `tns run android --release` and wait until app is deployed
        # IMPORTANT NOTE: `tns run android --release` Do NOT livesync by design!
        Device.uninstall_app(app_prefix="org.nativescript", platform=Platform.ANDROID)
        log = Tns.run_android(attributes={'--path': app_name,
                                          '--device': EMULATOR_ID,
                                          '--keyStorePath': ANDROID_KEYSTORE_PATH,
                                          '--keyStorePassword': ANDROID_KEYSTORE_PASS,
                                          '--keyStoreAlias': ANDROID_KEYSTORE_ALIAS,
                                          '--keyStoreAliasPassword': ANDROID_KEYSTORE_ALIAS_PASS,
                                          '--release': ''}, wait=False, assert_success=False)
        strings = ['Project successfully prepared', 'Project successfully built',
                   'Successfully installed on device with identifier', EMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=150, check_interval=10)
        # Verify app looks correct inside emulator
        Device.screen_match(device_name=EMULATOR_NAME,
                            device_id=EMULATOR_ID, expected_image='livesync-hello-world_home')
        # Kills `tns run android --release`
        Tns.kill()
        # Replace files
        ReplaceHelper.replace(app_name, change_js)
        ReplaceHelper.replace(app_name, change_css)
        ReplaceHelper.replace(app_name, change_xml)
        # Run `tns run android --release` again and make sure changes above are applied
        log = Tns.run_android(attributes={'--path': app_name,
                                          '--device': EMULATOR_ID,
                                          '--keyStorePath': ANDROID_KEYSTORE_PATH,
                                          '--keyStorePassword': ANDROID_KEYSTORE_PASS,
                                          '--keyStoreAlias': ANDROID_KEYSTORE_ALIAS,
                                          '--keyStoreAliasPassword': ANDROID_KEYSTORE_ALIAS_PASS,
                                          '--release': ''}, wait=False, assert_success=False)
        strings = ['Project successfully prepared', 'Project successfully built',
                   'Successfully installed on device with identifier',
                   'Successfully started on device with identifier',
                   'JS:', EMULATOR_ID]
        Tns.wait_for_log(log_file=log, string_list=strings, timeout=120)
        # Verify app looks is update after changes in js, css and xml
        Device.screen_match(device_name=EMULATOR_NAME, device_id=EMULATOR_ID,
                            expected_image='livesync-hello-world_js_css_xml')