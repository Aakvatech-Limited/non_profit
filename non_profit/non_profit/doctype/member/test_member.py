# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import importlib
import unittest


class TestMember(unittest.TestCase):
	def test_member_module_imports_with_payments_dependency(self):
		module = importlib.import_module("non_profit.non_profit.doctype.member.member")
		self.assertTrue(hasattr(module, "get_payment_gateway_controller"))
