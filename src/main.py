"""
Client application using Kivy.
"""

__author__ = 'Tiziano Bettio'
__license__ = 'MIT'
__version__ = '0.1'
__copyright__ = """Copyright (c) 2019 Tiziano Bettio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""

import hashlib
import os
import time
import ssl
import urllib.request as request
import urllib.error

import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
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
    Label:
        id: status_label
        size_hint: 1.0, 0.045
        text: app.status_text
        font_size: '14sp'
        bold: True
        italic: True
        background_color: [0.15, 0.45, 0.1, 1]
    Button:
        size_hint: 1.0, 0.85
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
    status_text = StringProperty()

    def open_door(self):
        self.status_text = 'State: trying to open...'
        https = int(self.config.get('Connection', 'https'))
        protocol = 'https' if https else 'http'
        address = self.config.get('Connection', 'address')
        port = self.config.get('Connection', 'port')
        base_url = f'{protocol}://{address}:{port}'
        try:
            kw = {'url': f'{base_url}/salt'}
            if kw['url'].startswith('https'):
                ctx = ssl.SSLContext()
                ctx.verify_mode = ssl.CERT_NONE
                kw['context'] = ctx
            salt = request.urlopen(**kw).read().decode()
        except urllib.error.URLError:
            self.status_text = 'State: failed to get salt'
            return False

        hm = hashlib.sha3_512()
        passphrase = self.config.get('Connection', 'passphrase') + salt
        hm.update(passphrase.encode())
        hashstring = hm.hexdigest()

        w = int().from_bytes(os.urandom(8), 'little') / (2 ** 64 - 1)
        time.sleep(w)
        url = f'{base_url}/open?{salt}={hashstring}'

        try:
            kw = {'url': url}
            if kw['url'].startswith('https'):
                ctx = ssl.SSLContext()
                ctx.verify_mode = ssl.CERT_NONE
                kw['context'] = ctx
            result = request.urlopen(**kw).read().decode()
        except urllib.error.URLError:
            self.status_text = 'State: failed to send open'
            return False

        result = "success" in result.lower()
        if result:
            self.status_text = 'State: open successful'
        else:
            self.status_text = f'State: invalid passphrase: ' \
                f'{self.config.get("Connection", "passphrase")}'
        return result

    @property
    def ival(self):
        return float(self.config.get('App Settings', 'ival'))

    @property
    def keep_open(self):
        return int(self.config.get('App Settings', 'keep'))

    # noinspection PyUnusedLocal
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
        self.status_text = 'State: unknown'
        return Interface()

    def build_config(self, config):
        config.setdefaults('Connection', {
            'https': 1,
            'address': 'gdo.tizilogic.com',
            'port': 443,
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
        if key in (27, 4):
            print('Back button pressed. Closing...')
            App.get_running_app().stop()
            return True
        else:
            return False

    def on_pause(self):
        return True


if __name__ == '__main__':
    GDOClient().run()
