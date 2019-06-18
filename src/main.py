import hashlib
import os
import time
import urllib.request as request
import urllib.error

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.settings import SettingsWithTabbedPanel
from kivy.core.window import Window
from kivy.clock import Clock

from settings import connection_settings_json
from settings import app_settings_json

kivy.require('1.11.0')

Builder.load_string('''
<Interface>:
    orientation: 'vertical'
    Button:
        size_hint: 1.0, 0.9
        text: 'Open Sesame!'
        font_size: '32sp'
        on_release: app.open_door()
        background_normal: ''
        background_color: [0.15, 0.45, 0.1, 1]
    Button:
        size_hint: 1.0, 0.095
        text: 'Settings'
        font_size: '14sp'
        bold: True
        on_release: app.open_settings()
        background_normal: ''
        background_color: [0.85, 0.35, 0.1, 1]
''')


class Interface(BoxLayout):
    pass


class GDOClient(App):
    def open_door(self):
        https = int(self.config.get('Connection', 'https'))
        protocol = 'https' if https else 'http'
        address = self.config.get('Connection', 'address')
        port = self.config.get('Connection', 'port')
        base_url = f'{protocol}://{address}:{port}'
        try:
            salt = request.urlopen(f'{base_url}/salt').read().decode()
        except urllib.error.URLError:
            return False

        hm = hashlib.sha3_512()
        passphrase = self.config.get('Connection', 'passphrase') + salt
        hm.update(passphrase.encode())
        hashstring = hm.hexdigest()

        w = int().from_bytes(os.urandom(8), 'little') / (2 ** 64 - 1)
        time.sleep(w)
        url = f'{base_url}/open?{salt}={hashstring}'

        try:
            result = request.urlopen(url).read().decode()
        except urllib.error.URLError:
            return False

        result = "success" in result.lower()
        return result

    @property
    def ival(self):
        return float(self.config.get('App Settings', 'ival'))

    @property
    def keep_open(self):
        return int(self.config.get('App Settings', 'keep'))

    def keep_open_thread(self, dt):
        if self.keep_open:
            self.open_door()
        Clock.schedule_once(self.keep_open_thread, self.ival)

    def build(self):
        self.settings_cls = SettingsWithTabbedPanel
        self.use_kivy_settings = False
        if int(self.config.get('App Settings', 'auto')):
            self.open_door()
        Clock.schedule_once(self.keep_open_thread, self.ival)
        Window.bind(on_keyboard=self.key_input)
        return Interface()

    def build_config(self, config):
        config.setdefaults('Connection', {
            'https': 1,
            'address': 'gdo.tizilogic.com',
            'port': 12321,
            'passphrase': 'OpenUp'
        })
        config.setdefaults('App Settings', {
            'auto': 0,
            'keep': 0,
            'ival': 10
        })

    def build_settings(self, settings):
        settings.add_json_panel('Connection',
                                self.config,
                                data=connection_settings_json)
        settings.add_json_panel('App',
                                self.config,
                                data=app_settings_json)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def key_input(self, window, key, scancode, codepoint, modifier):
        if key == 27:
            App.get_running_app().stop()
        else:
            return False

    def on_pause(self):
        return True


if __name__ == '__main__':
    GDOClient().run()
