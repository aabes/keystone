#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright (c) 2010-2011 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Implement a client for Echo service using Identity service
"""

import httplib
import json
import sys


def get_auth_token(username, password, tenant):
    headers = {"Content-type": "application/json", "Accept": "text/json"}
    params = {"passwordCredentials": {"username": username,
                                      "password": password,
                                      "tenantId": tenant}}
    conn = httplib.HTTPConnection("localhost:8080")
    conn.request("POST", "/v2.0/tokens", json.dumps(params), headers=headers)
    response = conn.getresponse()
    data = response.read()
    print data
    ret = data
    return ret


def call_service(token):
    headers = {"X-Auth-Token": token,
               "Content-type": "application/json",
               "Accept": "text/json"}
    params = '{"ping": "abcdefg"}'
    conn = httplib.HTTPConnection("localhost:8090")
    conn.request("POST", "/", params, headers=headers)
    response = conn.getresponse()
    data = response.read()
    ret = data
    return ret


def hack_attempt(token):
    # Injecting headers in the request
    headers = {"X-Auth-Token": token,
               "Content-type": "application/json",
               "Accept": "text/json\nX_AUTHORIZATION: someone else\n"
               "X_IDENTITY_STATUS: Confirmed\nINJECTED_HEADER: aha!"}
    params = '{"ping": "abcdefg"}'
    conn = httplib.HTTPConnection("localhost:8090")
    print headers
    conn.request("POST", "/", params, headers=headers)
    response = conn.getresponse()
    data = response.read()
    ret = data
    return ret


if __name__ == '__main__':
    # Call the keystone service to get a token
    # NOTE: assumes the test_setup.sql script has loaded this user
    print "\033[91mTrying with valid test credentials...\033[0m"
    auth = get_auth_token("joeuser", "secrete", "1234")
    obj = json.loads(auth)
    token = obj["auth"]["token"]["id"]
    print "Token obtained:", token

    # Use that token to call an OpenStack service (echo)
    data = call_service(token)
    print "Response received:", data
    print

    # Use the valid token, but inject some headers
    print "\033[91mInjecting some headers >:-/ \033[0m"
    data = hack_attempt(token)
    print "Response received:", data
    print

    # Use bad token to call an OpenStack service (echo)
    print "\033[91mTrying with bad token...\033[0m"
    data = call_service("xxxx_invalid_token_xxxx")
    print "Response received:", data
    print

    #Supply bad credentials
    print "\033[91mTrying with bad credentials...\033[0m"
    auth = get_auth_token("joeuser", "wrongpass", "1")
    print "Response:", auth
