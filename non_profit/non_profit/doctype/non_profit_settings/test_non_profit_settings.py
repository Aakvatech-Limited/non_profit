# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import importlib
import unittest
from pathlib import Path
import tomllib

from non_profit import hooks


class TestNonProfitSettings(unittest.TestCase):
	def test_required_apps_include_erpnext_and_payments(self):
		self.assertIn("erpnext", hooks.required_apps)
		self.assertIn("payments", hooks.required_apps)

	def test_required_apps_are_declared_in_pyproject(self):
		pyproject = self._get_pyproject()
		dependencies = pyproject["tool"]["bench"]["frappe-dependencies"]

		for app in hooks.required_apps:
			self.assertIn(app, dependencies)

	def test_frappe_app_dependencies_target_version_16(self):
		pyproject = self._get_pyproject()
		dependencies = pyproject["tool"]["bench"]["frappe-dependencies"]
		expected_range = ">=16.0.0,<17.0.0"

		for app in ("frappe", "erpnext", "payments"):
			self.assertEqual(dependencies.get(app), expected_range)

	def test_payments_utility_import_resolves(self):
		module = importlib.import_module("payments.utils")
		self.assertTrue(hasattr(module, "get_payment_gateway_controller"))

	def test_non_profit_settings_module_imports(self):
		module = importlib.import_module(
			"non_profit.non_profit.doctype.non_profit_settings.non_profit_settings"
		)
		self.assertTrue(hasattr(module, "get_payment_gateway_controller"))

	@staticmethod
	def _get_pyproject():
		repository_root = Path(__file__).resolve().parents[4]
		with (repository_root / "pyproject.toml").open("rb") as pyproject_file:
			return tomllib.load(pyproject_file)
