# -*- coding: utf-8 -*-

from .context import bot

import unittest


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_exists(self):
        self.assertTrue(bot.core.exists())


if __name__ == '__main__':
    unittest.main()
