import unittest

from core.base_class.BaseClass import BaseClass
from core.device.emulator import Emulator
from core.device.simulator import Simulator
from core.npm.npm import Npm
from core.osutils.os_type import OSType
from core.settings.settings import ANDROID_KEYSTORE_PATH, \
    ANDROID_KEYSTORE_PASS, ANDROID_KEYSTORE_ALIAS, ANDROID_KEYSTORE_ALIAS_PASS, EMULATOR_ID, CURRENT_OS, \
    IOS_RUNTIME_PATH, SIMULATOR_NAME, ANDROID_RUNTIME_PATH
from core.tns.replace_helper import ReplaceHelper
from core.tns.tns import Tns
from tests.webpack.helpers.helpers import Helpers


class WebPackHelloWorldJS(BaseClass):
    SIMULATOR_ID = ""

    image_original = 'hello-world-js'
    image_change = 'hello-world-js-js-css-xml'

    wp_run = ['Webpack compilation complete', 'Successfully installed']
    wp_errors = ['ERROR', 'Module not found', 'Error']

    xml_change = ['app/main-page.xml', 'TAP', 'TEST']
    js_change = ['app/main-view-model.js', 'taps', 'clicks']
    css_change = ['app/app.css', '18', '32']

    @classmethod
    def setUpClass(cls):
        BaseClass.setUpClass(cls.__name__)
        Emulator.stop()
        Emulator.ensure_available()

        Tns.create_app(cls.app_name, update_modules=True)
        Npm.install(package="nativescript-dev-webpack@next", option='--save-dev', folder=cls.app_name)
        Tns.platform_add_android(attributes={"--path": cls.app_name, "--frameworkPath": ANDROID_RUNTIME_PATH})

        if CURRENT_OS == OSType.OSX:
            Simulator.stop()
            cls.SIMULATOR_ID = Simulator.ensure_available(simulator_name=SIMULATOR_NAME)
            Tns.platform_add_ios(attributes={'--path': cls.app_name, '--frameworkPath': IOS_RUNTIME_PATH})

    def setUp(self):
        Tns.kill()
        Helpers.emulator_cleanup(app_name=self.app_name)

    @classmethod
    def tearDownClass(cls):
        BaseClass.tearDownClass()

    def test_001_android_build_release_with_bundle(self):
        Tns.build_android(attributes={"--path": self.app_name,
                                      "--keyStorePath": ANDROID_KEYSTORE_PATH,
                                      "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                      "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                      "--keyStoreAliasPassword": ANDROID_KEYSTORE_ALIAS_PASS,
                                      "--release": "",
                                      "--bundle": ""})

        Helpers.verify_size(app_name=self.app_name, config="js-android-bundle")
        Helpers.run_android_via_adb(app_name=self.app_name, config="release", image=self.image_original)

    @unittest.skipIf(CURRENT_OS != OSType.OSX, "Run only on macOS.")
    def test_001_ios_build_release_with_bundle(self):
        Tns.build_ios(attributes={"--path": self.app_name, "--release": "", "--for-device": "", "--bundle": ""})
        Helpers.verify_size(app_name=self.app_name, config="js-ios-bundle")

    def test_100_android_build_release_with_bundle_and_uglify(self):
        Tns.build_android(attributes={"--path": self.app_name,
                                      "--keyStorePath": ANDROID_KEYSTORE_PATH,
                                      "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                      "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                      "--keyStoreAliasPassword": ANDROID_KEYSTORE_ALIAS_PASS,
                                      "--release": "",
                                      "--bundle": "",
                                      "--env.uglify": ""})

        Helpers.verify_size(app_name=self.app_name, config="js-android-bundle-uglify")
        Helpers.run_android_via_adb(app_name=self.app_name, config="release", image=self.image_original)

    @unittest.skipIf(CURRENT_OS != OSType.OSX, "Run only on macOS.")
    def test_100_ios_build_release_with_bundle_and_uglify(self):
        Tns.build_ios(attributes={"--path": self.app_name, "--release": "", "--for-device": "", "--bundle": "",
                                  "--env.uglify": ""})

        Helpers.verify_size(app_name=self.app_name, config="js-ios-bundle-uglify")

    def test_110_android_build_release_with_bundle_and_snapshot(self):
        Tns.build_android(attributes={"--path": self.app_name,
                                      "--keyStorePath": ANDROID_KEYSTORE_PATH,
                                      "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                      "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                      "--keyStoreAliasPassword": ANDROID_KEYSTORE_ALIAS_PASS,
                                      "--release": "",
                                      "--bundle": "",
                                      "--env.snapshot": ""})

        Helpers.verify_size(app_name=self.app_name, config="js-android-bundle-snapshot")
        Helpers.run_android_via_adb(app_name=self.app_name, config="release", image=self.image_original)

    def test_120_android_build_release_with_bundle_and_snapshot_and_uglify(self):
        Tns.build_android(attributes={"--path": self.app_name,
                                      "--keyStorePath": ANDROID_KEYSTORE_PATH,
                                      "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                      "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                      "--keyStoreAliasPassword": ANDROID_KEYSTORE_ALIAS_PASS,
                                      "--release": "",
                                      "--bundle": "",
                                      "--env.uglify": "",
                                      "--env.snapshot": ""})

        Helpers.verify_size(app_name=self.app_name, config="js-android-bundle-uglify-snapshot")
        Helpers.run_android_via_adb(app_name=self.app_name, config="release", image=self.image_original)

    def test_200_run_android_with_bundle_sync_changes(self):
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_original)
        Tns.kill()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.js_change)
        ReplaceHelper.replace(self.app_name, self.xml_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=60)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_change)
        Tns.kill()

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.js_change)
        ReplaceHelper.rollback(self.app_name, self.xml_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_original)
        Tns.kill()

    @unittest.skipIf(CURRENT_OS != OSType.OSX, "Run only on macOS.")
    def test_200_run_ios_with_bundle_sync_changes(self):
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': ''}, wait=False,
                          assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original)
        Tns.kill()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.js_change)
        ReplaceHelper.replace(self.app_name, self.xml_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': ''}, wait=False,
                          assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=60)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_change)
        Tns.kill()

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.js_change)
        ReplaceHelper.rollback(self.app_name, self.xml_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': ''}, wait=False,
                          assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original)
        Tns.kill()

    def test_210_run_android_with_bundle_uglify_sync_changes(self):
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.uglify": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_original)
        Tns.kill()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.js_change)
        ReplaceHelper.replace(self.app_name, self.xml_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.uglify": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=60)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_change)
        Tns.kill()

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.js_change)
        ReplaceHelper.rollback(self.app_name, self.xml_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.uglify": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_original)
        Tns.kill()

    @unittest.skipIf(CURRENT_OS != OSType.OSX, "Run only on macOS.")
    def test_210_run_ios_with_bundle_uglify_sync_changes(self):
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': '', '--env.uglify': ''},
                          wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original)
        Tns.kill()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.js_change)
        ReplaceHelper.replace(self.app_name, self.xml_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': '', '--env.uglify': ''},
                          wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=60)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_change)
        Tns.kill()

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.js_change)
        ReplaceHelper.rollback(self.app_name, self.xml_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': '', '--env.uglify': ''},
                          wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original)
        Tns.kill()

    def test_220_run_android_with_bundle_snapshot_sync_changes(self):
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.snapshot": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_original)
        Tns.kill()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.js_change)
        ReplaceHelper.replace(self.app_name, self.xml_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.snapshot": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=60)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_change)
        Tns.kill()

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.js_change)
        ReplaceHelper.rollback(self.app_name, self.xml_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.snapshot": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_original)
        Tns.kill()

    @unittest.skipIf(CURRENT_OS != OSType.OSX, "Run only on macOS.")
    def test_220_run_ios_with_bundle_snapshot_sync_changes(self):
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': '', '--env.snapshot': ''},
                          wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original)
        Tns.kill()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.js_change)
        ReplaceHelper.replace(self.app_name, self.xml_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': '', '--env.snapshot': ''},
                          wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=60)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_change)
        Tns.kill()

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.js_change)
        ReplaceHelper.rollback(self.app_name, self.xml_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': '', '--env.snapshot': ''},
                          wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original)
        Tns.kill()

    def test_230_run_android_with_bundle_snapshot_and_uglify_sync_changes(self):
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.snapshot": "",
                                          "--env.uglify": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_original)
        Tns.kill()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.js_change)
        ReplaceHelper.replace(self.app_name, self.xml_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.snapshot": "",
                                          "--env.uglify": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=60)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_change)
        Tns.kill()

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.js_change)
        ReplaceHelper.rollback(self.app_name, self.xml_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.snapshot": "",
                                          "--env.uglify": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.android_screen_match(app_name=self.app_name, image=self.image_original)
        Tns.kill()

    @unittest.skipIf(CURRENT_OS != OSType.OSX, "Run only on macOS.")
    def test_230_run_ios_with_bundle_snapshot_and_uglify_sync_changes(self):
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': '', '--env.snapshot': '',
                                      '--env.uglify': ''}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original)
        Tns.kill()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.js_change)
        ReplaceHelper.replace(self.app_name, self.xml_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': '', '--env.snapshot': '',
                                      '--env.uglify': ''}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=60)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_change)
        Tns.kill()

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.js_change)
        ReplaceHelper.rollback(self.app_name, self.xml_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': '', '--env.snapshot': '',
                                      '--env.uglify': ''}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=self.wp_run, not_existing_string_list=self.wp_errors, timeout=180)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original)
        Tns.kill()

    def test_400_build_with_bundle_without_plugin(self):
        Tns.create_app(self.app_name)
        output = Tns.build_android(attributes={"--path": self.app_name, "--bundle": ""}, assert_success=False)
        assert "Passing --bundle requires a bundling plugin." in output
        assert "No bundling plugin found or the specified bundling plugin is invalid." in output
