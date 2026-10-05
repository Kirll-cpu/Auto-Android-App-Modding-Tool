import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from github_chat import (  # noqa: E402
    BOT_PREFIX,
    build_messages,
    extract_command,
)


class ExtractCommandTests(unittest.TestCase):
    def test_extracts_message_after_command(self):
        self.assertEqual(extract_command("/chat Hello there"), "Hello there")

    def test_ignores_non_command_and_empty_command(self):
        self.assertIsNone(extract_command("Hello there"))
        self.assertIsNone(extract_command("/chat "))


class BuildMessagesTests(unittest.TestCase):
    def test_builds_chronological_chat_and_skips_unrelated_comments(self):
        comments = [
            {
                "id": 3,
                "created_at": "2025-01-03T00:00:00Z",
                "user": {"login": "owner"},
                "author_association": "OWNER",
                "body": "/chat Second question",
            },
            {
                "id": 2,
                "created_at": "2025-01-02T00:00:00Z",
                "user": {"login": "github-actions[bot]", "type": "Bot"},
                "author_association": "NONE",
                "body": BOT_PREFIX + "First answer",
            },
            {
                "id": 1,
                "created_at": "2025-01-01T00:00:00Z",
                "user": {"login": "owner"},
                "author_association": "OWNER",
                "body": "/chat First question",
            },
            {
                "id": 4,
                "created_at": "2025-01-04T00:00:00Z",
                "user": {"login": "visitor"},
                "author_association": "NONE",
                "body": "An unrelated comment",
            },
        ]

        self.assertEqual(
            build_messages(comments, "3"),
            [
                {"role": "user", "content": "First question"},
                {"role": "assistant", "content": "First answer"},
                {"role": "user", "content": "Second question"},
            ],
        )

    def test_rejects_unauthorized_trigger_comment(self):
        comments = [
            {
                "id": 1,
                "created_at": "2025-01-01T00:00:00Z",
                "user": {"login": "visitor"},
                "author_association": "NONE",
                "body": "/chat Hello",
            }
        ]
        with self.assertRaisesRegex(ValueError, "not an authorized"):
            build_messages(comments, "1")

    def test_requires_trigger_comment_in_history(self):
        with self.assertRaisesRegex(ValueError, "Could not find"):
            build_messages([], "123")


if __name__ == "__main__":
    unittest.main()
