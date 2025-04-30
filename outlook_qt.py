#!/usr/bin/python3
#
# MIT License
#
# Copyright (c) 2025 Aditya Garg
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import trustme
from msal import PublicClientApplication
import http.server
import os
import sys
import threading
import urllib.parse
import tempfile
import random
import keyring
import ssl


from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QLoggingCategory


ClientId = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
Scopes = ['https://outlook.office.com/POP.AccessAsUser.All','https://outlook.office.com/IMAP.AccessAsUser.All','https://outlook.office.com/SMTP.Send']
ServiceName = "git-credential-outlook"

def save_refresh_token(refresh_token):
    keyring.set_password(ServiceName, "refresh_token", refresh_token)

def load_refresh_token():
    return keyring.get_password(ServiceName, "refresh_token")

app = PublicClientApplication(ClientId)

if not "--authenticate" in sys.argv:

    old_refresh_token = load_refresh_token()

    if old_refresh_token is None:
        sys.exit("No refresh token found.\nPlease authenticate first by running with --authenticate.")

    token = app.acquire_token_by_refresh_token(old_refresh_token,Scopes)

    if 'error' in token:
        print(token)
        sys.exit("Failed to get access token")

    print(f"password={token['access_token']}")
    sys.exit(0)

if "--authenticate" and not "--device" in sys.argv:

    random_port = random.randint(1024, 65535)
    redirect_uri = f"https://localhost:{random_port}/"

    url = app.get_authorization_request_url(Scopes, redirect_uri=redirect_uri)

    print("Navigate to the following url in a web browser, if doesn't open automatically:\n")
    print(f"{url}\n")

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            # Override to prevent logging to console
            pass
        def do_GET(self):
            parsed_url = urllib.parse.urlparse(self.path)
            parsed_query = urllib.parse.parse_qs(parsed_url.query)
            global code
            code = parsed_query.get('code', [''])[0]
            response_body = b'Success. You may close this window now.\r\n'
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(response_body))
            self.end_headers()
            self.wfile.write(response_body)

            global httpd
            threading.Thread(target=lambda: httpd.shutdown()).start()


    code = ''

    ca = trustme.CA()
    cert_file = os.path.join(tempfile.gettempdir(), "cert.crt")
    server_cert = ca.issue_cert("localhost")
    server_cert.private_key_and_cert_chain_pem.write_to_path(cert_file)

    server_address = ('', random_port)
    httpd = http.server.HTTPServer(server_address, Handler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file)
    httpd.socket = context.wrap_socket(
        httpd.socket,
        server_side=True,
    )
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    if "--verbose" in sys.argv:
        loglevel = 0
    else:
        loglevel = 3
        QLoggingCategory("qt.webenginecontext").setFilterRules("*.info=false") # Suppress info logs
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = f"--enable-logging --log-level={loglevel} --ignore-certificate-errors"
    class BrowserWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("OAuth2 Login")
            self.resize(800, 600)
            self.browser = QWebEngineView()
            self.setCentralWidget(self.browser)
            self.browser.load(QUrl(url))
            self.show()

    webapp = QApplication(sys.argv)
    window = BrowserWindow()
    webapp.exec()

    token = app.acquire_token_by_authorization_code(code, Scopes, redirect_uri=redirect_uri)
    os.remove(cert_file)

elif "--authenticate" and "--device" in sys.argv:

    # Device code flow
    device_flow = app.initiate_device_flow(scopes=Scopes)
    if "error" in device_flow:
        sys.exit(f"Failed to initiate device flow: {device_flow['error_description']}")

    print(f"To authenticate, visit {device_flow['verification_uri']} and enter the code: {device_flow['user_code']}")
    token = app.acquire_token_by_device_flow(device_flow)

if "error" in token:
    print(token)
    sys.exit("\nFailed to get access token")

print('Saved refresh token to keyring')
save_refresh_token(token['refresh_token'])
