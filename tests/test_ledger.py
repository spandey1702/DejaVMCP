import unittest

from ledger import DecisionLedger


class DecisionLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = DecisionLedger(storage_path=None)

    def test_claim_task_prevents_race(self) -> None:
        self.ledger.create_task("task-1", "Investigate bug")
        self.ledger.claim_task("task-1", "agent-a")
        with self.assertRaises(ValueError):
            self.ledger.claim_task("task-1", "agent-b")

    def test_record_decision_and_search_context(self) -> None:
        self.ledger.create_task("task-2", "Plan rollout")
        self.ledger.record_decision(
            "task-2",
            "agent-b",
            "Use a circuit breaker",
            "Repeat failures point to dependency flapping.",
            "recommended",
        )
        results = self.ledger.search_context("circuit breaker")
        self.assertTrue(any(result["decision"] == "Use a circuit breaker" for result in results))


if __name__ == "__main__":
    unittest.main()
