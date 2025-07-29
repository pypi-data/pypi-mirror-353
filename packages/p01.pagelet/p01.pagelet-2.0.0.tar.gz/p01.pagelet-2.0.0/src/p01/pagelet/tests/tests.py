###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Tests
$Id: tests.py 5168 2025-03-06 00:12:13Z felipe.souza $
"""
from __future__ import absolute_import
from __future__ import print_function

__docformat__ = "reStructuredText"

import unittest
import doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('checker.txt',
                             globs={'print_function': print_function,
                                    'absolute_import': absolute_import}),
    ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
