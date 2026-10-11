import unittest
from unittest.mock import patch


class TestChatbotIntents(unittest.TestCase):

    def _call(self, q, user_id=None):
        with patch("services.chatbot_service.db"):
            from services.chatbot_service import ChatbotService
            return ChatbotService.answer(q, user_id=user_id)

    def test_greeting(self):
        self.assertEqual(self._call("Hello")["intent"], "greeting")

    def test_help(self):
        self.assertEqual(self._call("What can you do?")["intent"], "help")

    def test_count(self):
        with patch("services.chatbot_service.db") as mock_db:
            mock_db.Scholarships.count_documents.return_value = 93
            from services.chatbot_service import ChatbotService
            res = ChatbotService.answer("How many scholarships available?")
            self.assertEqual(res["intent"], "count")
            self.assertIn("93", res["answer"])

    def test_empty(self):
        self.assertEqual(self._call("")["type"], "empty")

    def test_eligibility_needs_login(self):
        res = self._call("Am I eligible for National Merit?")
        self.assertEqual(res["intent"], "eligibility")
        self.assertIn("log in", res["answer"].lower())


if __name__ == "__main__":
    unittest.main()