from pathlib import Path
from html.parser import HTMLParser
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")


class TextCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)


class SiteContentTests(unittest.TestCase):
    def test_homepage_leads_with_workflow_outcome_and_clear_review_cta(self):
        self.assertIn(
            "<title>Workflow Automation for Arizona Businesses | Copper Canyon Concepts</title>",
            INDEX,
        )
        self.assertRegex(
            INDEX,
            r'<link rel="canonical" href="https://coppercanyonconcepts\.com/">',
        )
        self.assertIn(
            "Fix the handoffs that delay quotes, jobs, and invoices.",
            INDEX,
        )
        self.assertIn(
            "Workflow automation for Arizona small and midsize businesses",
            INDEX,
        )
        self.assertIn("Request a 20 minute workflow review", INDEX)
        self.assertIn("See a sample pilot plan", INDEX)
        self.assertIn(
            "You will leave with a clear next step, even if automation is not the answer.",
            INDEX,
        )
        self.assertNotIn("Compare workflows", INDEX)
        self.assertEqual(len(re.findall(r"<h1\b", INDEX)), 1)

    def test_homepage_defines_the_workflow_review_and_pilot_plan(self):
        self.assertIn('id="pilot-plan"', INDEX)
        self.assertIn("Workflow Review and Pilot Plan", INDEX)
        for deliverable in (
            "Current workflow map",
            "Baseline measurement plan",
            "Human approval points",
            "Access and data risk map",
            "Recommended bounded pilot",
            "Implementation estimate",
            "Proceed, revise, or stop decision",
        ):
            with self.subTest(deliverable=deliverable):
                self.assertIn(deliverable, INDEX)
        self.assertIn("paid diagnostic", INDEX)
        self.assertIn("No commitment to automate", INDEX)

    def test_homepage_shows_an_honest_closeout_to_invoice_sample(self):
        self.assertIn('id="sample-workflow"', INDEX)
        self.assertIn("Closeout to Invoice Readiness", INDEX)
        self.assertIn("Illustrative sample, not client work", INDEX)
        for stage in (
            "Work marked complete",
            "Required records checked",
            "Missing items routed",
            "Human approval recorded",
            "Invoice ready packet prepared",
            "Exceptions remain visible",
        ):
            with self.subTest(stage=stage):
                self.assertIn(stage, INDEX)
        self.assertIn("Nothing is sent or approved automatically", INDEX)
        self.assertIn("No savings or performance result is claimed", INDEX)

    def test_homepage_preserves_navigation_accessibility_and_privacy_boundaries(self):
        ids = set(re.findall(r'\bid="([^"]+)"', INDEX))
        internal_targets = re.findall(r'href="#([^"]+)"', INDEX)
        self.assertTrue(internal_targets)
        self.assertTrue(set(internal_targets).issubset(ids))
        self.assertIn('<ul role="list">', INDEX)
        self.assertRegex(
            INDEX,
            r'<ol class="workflow_path"[^>]*role="list"',
        )
        self.assertNotIn("<script", INDEX.lower())
        collector = TextCollector()
        collector.feed(INDEX)
        public_text = " ".join(collector.text)
        self.assertIsNone(re.search(r"[A-Za-z]-[A-Za-z]", public_text))


if __name__ == "__main__":
    unittest.main()
