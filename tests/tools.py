import unittest

from mcp import Client

from collaborative_mcp.server import mcp


class TestMCPTools(unittest.IsolatedAsyncioTestCase):
    async def test_propose_and_retrieve(self):
        async with Client(mcp, raise_exceptions=True) as client:
            result = await client.call_tool(
                "propose_command",
                {"command": "printf BEFORE"},
            )

            self.assertFalse(result.is_error)

            proposal = result.structured_content

            self.assertEqual(proposal["permission"], "ask")
            self.assertEqual(proposal["status"], "pending")

            details = await client.call_tool(
                "get_operation",
                {"operation_id": proposal["operation_id"]},
            )

            self.assertFalse(details.is_error)
            self.assertEqual(
                details.structured_content["original_command"],
                "printf BEFORE",
            )

    async def test_allowed_command(self):
        async with Client(mcp, raise_exceptions=True) as client:
            result = await client.call_tool(
                "propose_command",
                {"command": "pwd"},
            )

            self.assertFalse(result.is_error)
            self.assertEqual(
                result.structured_content["status"],
                "approved",
            )


if __name__ == "__main__":
    unittest.main()
