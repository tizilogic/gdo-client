import json

connection_settings_json = json.dumps([
    {'type': 'title',
     'title': 'Connection settings'},
    {'type': 'bool',
     'title': 'Use HTTPS',
     'desc': 'Whether to use HTTPS',
     'section': 'Connection',
     'key': 'https'},
    {'type': 'string',
     'title': 'Address',
     'desc': 'IP or FQDN of the server',
     'section': 'Connection',
     'key': 'address'},
    {'type': 'numeric',
     'title': 'Port',
     'desc': 'The port number the server is listening on',
     'section': 'Connection',
     'key': 'port'},
    {'type': 'string',
     'title': 'Passphrase',
     'desc': 'The passphrase used to open the door',
     'section': 'Connection',
     'key': 'passphrase'}])

app_settings_json = json.dumps([
    {'type': 'title',
     'title': 'App settings'},
    {'type': 'bool',
     'title': 'Auto Open',
     'desc': 'Whether to send the open command to the server upon start',
     'section': 'App Settings',
     'key': 'auto'},
    {'type': 'bool',
     'title': 'Keep Open',
     'desc': 'Keeps the door open as long as the App is running',
     'section': 'App Settings',
     'key': 'keep'},
    {'type': 'numeric',
     'title': 'Keep Open Interval',
     'desc': 'If "Keep Open" is enabled, how many seconds between sending the '
             'open command.',
     'section': 'App Settings',
     'key': 'ival'}])