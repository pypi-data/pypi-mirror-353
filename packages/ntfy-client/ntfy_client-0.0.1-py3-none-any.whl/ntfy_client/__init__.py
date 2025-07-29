#!/usr/bin/env python

# NTFY API
# specification: https://docs.ntfy.sh/subscribe/api/

# original:
# https://github.com/iacchus/python-pushover-open-client/blob/main/src/python_pushover_open_client/__init__.py

import datetime
import functools
import json
import os
import requests
import shlex
import shutil
import subprocess
import sys
import types
# import typing

#cli:
import argparse
import base64
import json
import os
import pathlib
import pprint
import sys
import typing

import requests

from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

import websocket

FUNCTION = types.FunctionType

#  DEBUG: bool = False
DEBUG: bool = True

if DEBUG:
    websocket.enableTrace(True)

# from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

# if sys.version_info[:2] >= (3, 8):
#    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
#    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
# else:
#    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "ntfy-client"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


#  NTFY_CLI_DEBUG = False  # set to True to output debugging information
#  NTFY_CLI_DEBUG = os.environ.get('NTFY_CLI_DEBUG', default=NTFY_CLI_DEBUG)

# FIXME: check what is not constants anymore and write these in lowercase

# let's prepend all environment variables with our namespace ("NTFY_", by now)
NTFY_SERVER_HOSTNAME = os.environ.get('NTFY_SERVER_HOSTNAME')
NTFY_TOPIC = os.environ.get('NTFY_TOPIC')
NTFY_TOKEN = os.environ.get('NTFY_TOKEN')
#  NTFY_URL_HTTPS = os.environ.get('NTFY_URL_HTTPS')
#  NTFY_URL_WSS = os.environ.get('NTFY_URL_WSS')



#  NTFY_DEFAULT_=os.environ.get('NTFY_DEFAULT_', default=)  # COPYME!
#  os.environ.get('NTFY_MESSAGE_BODY')
DEFAULT_MESSAGE = os.environ.get('NTFY_DEFAULT_MESSAGE', default=sys.stdin)
DEFAULT_TITLE = os.environ.get('NTFY_DEFAULT_TITLE', default="Sent via ntfy-cli")
#  DEFAULT_TITLE = os.environ.get('NTFY_DEFAULT_TITLE', default="Sent via ntfy-cli")

#  NTFY_ICON = "https://public.kassius.org/python-logo.png"
NTFY_ICON = os.environ.get('NTFY_ICON')

PRIORITIES = {"urgent", "high", "default", "low", "min"}
YES_NO = {"yes", "no"}
ON_OFF = {"1", "0"}

FILE_RECEIVED_MESSAGE = "You received a file: {file_name}"

default_config_dict = {
    "hostname":  NTFY_SERVER_HOSTNAME,
    "topic": NTFY_TOPIC,
    "token": NTFY_TOKEN,

    "title": "from ntfycli.py",
    "message": "defmsg",
    "priority": "default",
    "tags": [],
    "markdown": None,
    "delay": None,
    "actions": None,
    "click": None,
    "attach": None,
    "filename": None,
    "email": None,
    "call": None,

    "cache": None,
    "firebase": None,
    "unifiedpush": None,

    "authorization": None,
    "content_type": None
    }

argument_parser = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        description='Send ntfy notification',
        epilog="https://github.com/iacchus/ntfy-cli"
        )

argument_parser.add_argument("-t", "--title", default=DEFAULT_TITLE)
argument_parser.add_argument("-m", "--message", default=DEFAULT_MESSAGE)
argument_parser.add_argument("-p", "--priority", choices=PRIORITIES)
argument_parser.add_argument("-x", "--tags", "--tag", action="extend",
                             nargs="+", type=str)
argument_parser.add_argument("-d", "--delay", default=None)
argument_parser.add_argument("-A", "--actions", "--action", action="extend",
                             nargs="+", type=str)
argument_parser.add_argument("-c", "--click", default=None)
argument_parser.add_argument("-k", "--markdown", action="store_const",
                             const="yes")
argument_parser.add_argument("-i", "--icon", default=NTFY_ICON,
                             help="Notification icon URL")
# FIXME: this here:
#  argument_parser.add_argument("-f", "--file", type=str,
argument_parser.add_argument("-f", "--file", default="",
                             help="Attach a local file")
argument_parser.add_argument("-a", "--attach",
                             help="Attach a file from an URL", default=None)
argument_parser.add_argument("-b", "--firebase", default=None,
                             choices=YES_NO, help="Use Firebase")
argument_parser.add_argument("-u", "--unifiedpush", default=None,
                             choices=YES_NO, help="Use UnifiedPush")
argument_parser.add_argument("-F", "--filename",
                             help="Send message as file with <filename>")
argument_parser.add_argument("-E", "--email",
                             help="Send message to <email>")
argument_parser.add_argument("-V", "--call",
                             help="Phone number for phone calls.")
argument_parser.add_argument("-C", "--cache", choices=YES_NO, default=None,
                             help="Use cache for messages")
argument_parser.add_argument("-I", "--poll-id",
                             help="Internal parameter, used for i*OS "
                             "push notifications")
argument_parser.add_argument("-T", "--content-type",
                             help="Set the 'Content-Type' header manually",
                             default=None)

args = argument_parser.parse_args()

MESSAGE_BODY = args.message


# FIXME:
# Group mutually exclusive options (argparse docs)
# those are:
# * X-UnifiedPush vs X-Firebase
# * Authorization Basic vs Bearer
# * Authorization Username (envvar/arg) vs Bearer auth
# * Authorization Password (envvar/arg) vs Bearer
# * Authorization Token (envvar/arg) vs Basic auth
# * X-Attach vs X-File
# * X-Markdown vs Content-Type != "text/markdown"

# FIXME: UnifiedPush vs --file sending file as message

# TODO; sanitize parameters?

# TODO: CONFIG PRIORITY
# (first in this list has greater priority)
# 
# command-line arguments (user)
# environment variables (user, file or inline)
# ~/.notify-cli.conf (user, file)
# /etc/notify-cli.conf (system, file)
# (script, hardcoded defaults)


#  class NTFYCommandLineInterface:
class NTFYClient:

    hostname: str
    topic: str
    token: str

    title: str
    message: str
    priority: str
    tags: list[str]  # ", ".join(tags)
    markdown: bool
    delay: str
    actions: list[str]  # "; ".join(actions)
    click: str
    attach: str
    filename: str
    email: str
    call: str

    cache: str
    firebase: str
    unifiedpush: str

    authorization: str | tuple[str, str]
    content_type: str

    def __init__(self, hostname, topic, token, args):
        self.hostname = hostname
        self.topic = topic
        self.token = token

        self.message = args.message or sys.stdin  # FIXME
        self.args = args  # FIXME: remove this: process it yourself

        self.url_https = f"https://{hostname}/{topic}"
        self.url_wss = f"wss://{hostname}/{topic}/ws"

        self.authorization = self.make_auth_token(method="basic")
        self.headers = self.make_headers(args)

    def pub(self, message=None):
        file_path = pathlib.Path(self.args.file)

        if file_path.is_file():
            self.headers.update({
                "X-Title": "File received (via ntfy)",
                "X-Message": FILE_RECEIVED_MESSAGE.format(file_name=self.args.filename
                                                          or file_path.name),
                "X-tags": "gift",
                "X-Filename": self.args.filename or file_path.name
                })
        elif args.file and not file_path.is_file():
            print(f"Error: file '{file_path.absolute()}' not found, exiting.")
            exit(1)

        data = open(file_path.absolute(), "rb") if self.args.file else MESSAGE_BODY
        response = requests.post(url=self.url_https,
                                 data=data,
                                 headers=self.headers)

        return response

    def make_headers(self, args):
        all_headers = {
                #  "X-Title": args.title or DEFAULT_MESSAGE_TITLE,
                "X-Title": args.title,
                "X-Icon": args.icon or None, #ICON_IMAGE_URL,
                "X-Priority": args.priority or None,
                "X-Tags": ",".join(args.tags if args.tags else []),
                "X-Markdown": args.markdown or None,
                "X-Delay": args.delay or None,
                "X-Actions": "; ".join(args.actions if args.actions else []),
                "X-Click": args.click or None,
                "X-Attach": args.attach,
                "X-Filename": args.filename or None,
                "X-Email": args.email or None,
                "X-Call": args.call or None,
                "X-Cache": args.cache or None,
                "X-Firebase": args.firebase or None,
                "X-UnifiedPush": args.unifiedpush or None,
                "X-Poll-ID": args.poll_id or None,
                "Authorization": self.authorization,
                "Content-Type": args.content_type or None,
                }

        headers = {key: value for key, value in all_headers.items() if value}
        print(all_headers)
        print(headers)

        return headers

    def make_auth_token(self, method="basic"):
        if method == "basic":
            auth_string = f":{self.token}"  # str: "empty_username:token"
            auth_string_bytes = auth_string.encode("ascii")
            auth_string_base64 = base64.b64encode(auth_string_bytes).decode("utf-8")

            authorization = f"Basic {auth_string_base64}"
        elif method == "query_param":
            # FIXME: deduplicate this code with the above
            auth_string = f":{self.token}"  # str: "empty_username:token"
            auth_string_bytes = auth_string.encode("ascii")
            auth_header_basic = \
                    base64.b64encode(auth_string_bytes).decode("utf-8")
            auth_string_base64 = base64.b64encode(auth_string_bytes).decode("utf-8")

            authorization = f"Basic {auth_string_base64}"
            auth_header_query_param_key = "auth"
            auth_header_query_param_value = \
                    base64.b64encode(auth_header_basic
                                     .encode("ascii")).decode("utf-8")
            authorization = (auth_header_query_param_key,
                             auth_header_query_param_value)
        else:
            authorization = f"Bearer {self.token}"

        return authorization

ntfycli = NTFYClient(hostname=NTFY_SERVER_HOSTNAME,
                                   topic=NTFY_TOPIC,
                                   token=NTFY_TOKEN,
                                   args=args)

r = ntfycli.pub()

#  ntfycli = NTFYCommandLineInterface(hostname=NTFY_SERVER_HOSTNAME,
#                                     topic=NTFY_TOPIC,
#                                     token=NTFY_TOKEN,
#                                     args=args)

#  ntfycli.pub(message=data)
#  r = ntfycli.pub()
#  data = open(file_path.absolute(), "rb") if args.file else MESSAGE_BODY
#  r = requests.post(url=NTFY_URL_HTTPS, data=data, headers=headers_cleared)  # pyright: ignore

response_data = json.dumps(r.json(), indent=2)
print("Response data:", response_data, sep="\n")
