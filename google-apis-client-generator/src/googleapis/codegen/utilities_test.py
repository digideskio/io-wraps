#!/usr/bin/python
#
# Copyright 2010 Google Inc. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Tests for utilities.py."""

__author__ = 'aiuto@google.com (Tony Aiuto)'


from google.apputils import basetest

from googleapis.codegen import utilities


class UtilitiesTest(basetest.TestCase):

  def testCamelCase(self):
    """Basic CamelCase functionality."""
    self.assertEquals('HelloWorld', utilities.CamelCase('hello_world'))
    self.assertEquals('HelloWorld', utilities.CamelCase('hello-world'))
    self.assertEquals('HelloWorld', utilities.CamelCase('helloWorld'))
    self.assertEquals('HelloWorld', utilities.CamelCase('Hello_world'))
    self.assertEquals('HelloWorld', utilities.CamelCase('_hello_world'))
    self.assertEquals('HelloWorld', utilities.CamelCase('helloWorld'))
    self.assertEquals('HelloWorld', utilities.CamelCase('hello.world'))
    self.assertEquals('HELLOWORLD', utilities.CamelCase('HELLO_WORLD'))


if __name__ == '__main__':
  basetest.main()
