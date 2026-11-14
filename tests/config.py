import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from collaborative_mcp.models import Permission
from collaborative_mcp.policy import load_policy


class TestPolicyConfig(unittest.TestCase):
    def test_load_valid_policy(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text(
                '[permissions]\n'
                'shell_default = "ask"\n'
                'file_write_default = "ask"\n'
                '[permissions.shell_rules]\n'
                'pwd = "allow"\n'
                '"printf DENIED" = "deny"\n'
            )

            policy = load_policy(path)

            self.assertEqual(policy.shell_default, Permission.ASK)
            self.assertEqual(
                policy.shell_rules,
                (
                    ("pwd", Permission.ALLOW),
                    ("printf DENIED", Permission.DENY),
                ),
            )

    def test_invalid_permission_rejected(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text(
                '[permissions]\nshell_default = "yes"\n'
            )

            with self.assertRaises(ValueError):
                load_policy(path)

    def test_unknown_setting_rejected(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text(
                '[permissions]\nshell_defaut = "allow"\n'
            )

            with self.assertRaises(ValueError):
                load_policy(path)


if __name__ == "__main__":
    unittest.main()
