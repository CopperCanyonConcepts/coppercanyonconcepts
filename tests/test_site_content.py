from pathlib import Path
from html.parser import HTMLParser
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
CONTACT_PATH = ROOT / "contact.html"
CONTACT = CONTACT_PATH.read_text(encoding="utf-8") if CONTACT_PATH.exists() else ""
CONTACT_SCRIPT_PATH = ROOT / "contact.js"
CONTACT_SCRIPT = CONTACT_SCRIPT_PATH.read_text(encoding="utf-8") if CONTACT_SCRIPT_PATH.exists() else ""
PRIVACY = (ROOT / "privacy.html").read_text(encoding="utf-8")
STYLES = (ROOT / "styles.css").read_text(encoding="utf-8")


class TextCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)


def relative_luminance(hex_color):
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    converted = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * converted[0] + 0.7152 * converted[1] + 0.0722 * converted[2]


def contrast_ratio(first, second):
    light, dark = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class SiteContentTests(unittest.TestCase):
    def test_homepage_leads_with_broad_business_problem_solving_offer(self):
        self.assertIn(
            "<title>Business Development and Operations | Copper Canyon Concepts</title>",
            INDEX,
        )
        self.assertRegex(
            INDEX,
            r'<link rel="canonical" href="https://coppercanyonconcepts\.com/">',
        )
        self.assertIn(
            "Bring us the problem. We will help build the solution.",
            INDEX,
        )
        self.assertIn("Business creation, websites, and connected operations", INDEX)
        self.assertIn("Tell us what needs to be solved", INDEX)
        self.assertIn("Explore our services", INDEX)
        self.assertNotIn("Compare workflows", INDEX)
        self.assertEqual(len(re.findall(r"<h1\b", INDEX)), 1)

    def test_homepage_names_each_approved_service_area(self):
        for service in (
            "Business creation",
            "Website development",
            "Project workflows",
            "CRM integration",
            "Email automation",
            "Marketing support",
        ):
            with self.subTest(service=service):
                self.assertIn(service, INDEX)
        self.assertIn("Problem Review and Solution Plan", INDEX)
        self.assertIn("A problem does not need to arrive with a technical specification", INDEX)

    def test_homepage_omits_removed_banner_and_closeout_sample(self):
        self.assertNotIn('class="principles"', INDEX)
        self.assertNotIn('id="sample-workflow"', INDEX)
        self.assertNotIn("Closeout to Invoice Readiness", INDEX)
        for removed_phrase in (
            "Start with the real problem",
            "Build for practical use",
            "Owners stay in control",
        ):
            with self.subTest(removed_phrase=removed_phrase):
                self.assertNotIn(removed_phrase, INDEX)

    def test_solution_plan_is_short_and_scannable(self):
        match = re.search(
            r'<div class="pilot_deliverables">(.*?)</div>\s*</section>',
            INDEX,
            re.DOTALL,
        )
        if match is None:
            self.fail("pilot deliverables section was not found")
        deliverables = match.group(1)
        self.assertEqual(deliverables.count("<li>"), 4)
        for item in (
            "Goal and problem definition",
            "Current tools and constraints",
            "Recommended solution and project phases",
            "Scope, estimate, and proceed decision",
        ):
            with self.subTest(item=item):
                self.assertIn(item, deliverables)

    def test_ownership_section_is_compact_accountable_and_responsive(self):
        self.assertIn("Experienced ownership. Accountable delivery.", INDEX)
        self.assertIn("Operating leadership", INDEX)
        self.assertIn("Owner accountability", INDEX)
        self.assertIn(
            "Human owners retain final authority over access, spending, publishing, and customer commitments.",
            INDEX,
        )
        self.assertIn(
            ".team_layout {\n  display: grid;\n  grid-template-columns: 1fr;",
            STYLES,
        )
        self.assertIn(
            ".team_story {\n  display: grid;\n  grid-template-columns: 1fr 1fr;",
            STYLES,
        )
        self.assertRegex(
            STYLES,
            r'(?s)@media \(max-width: 620px\).*?\.team_story \{\s*grid-template-columns: 1fr;',
        )

    def test_homepage_preserves_navigation_accessibility_and_privacy_boundaries(self):
        ids = set(re.findall(r'\bid="([^"]+)"', INDEX))
        internal_targets = re.findall(r'href="#([^"]+)"', INDEX)
        self.assertTrue(internal_targets)
        self.assertTrue(set(internal_targets).issubset(ids))
        self.assertIn('<ul role="list">', INDEX)
        self.assertNotIn('<div class="pilot_deliverables" aria-label=', INDEX)
        self.assertRegex(
            INDEX,
            r'<ol class="method_steps"[^>]*role="list"',
        )
        self.assertNotIn("<script", INDEX.lower())
        collector = TextCollector()
        collector.feed(INDEX)
        public_text = " ".join(collector.text)
        self.assertIsNone(re.search(r"[A-Za-z]-[A-Za-z]", public_text))

    def test_contact_page_collects_business_context_without_third_party_submission(self):
        self.assertTrue(CONTACT)
        self.assertIn("Tell us what needs to be solved", CONTACT)
        self.assertIn('<form id="inquiry-form"', CONTACT)
        for field in (
            'name="contact_name"',
            'name="email"',
            'name="company"',
            'name="business_stage"',
            'name="help_areas"',
            'name="problem"',
            'name="current_tools"',
            'name="desired_result"',
            'name="timeframe"',
            'name="safe_to_email"',
        ):
            with self.subTest(field=field):
                self.assertIn(field, CONTACT)
        self.assertNotRegex(CONTACT, r'<form[^>]+action="https?://')
        self.assertIn('<form id="inquiry-form" action="mailto:operations@coppercanyonconcepts.com" method="post" enctype="text/plain">', CONTACT)
        self.assertRegex(CONTACT, r'<button[^>]+type="submit"[^>]+disabled')
        self.assertIn('src="contact.js"', CONTACT)
        self.assertIn('href="#inquiry-form">Start the inquiry</a>', CONTACT)
        self.assertIn("Prepare my inquiry", CONTACT)
        self.assertIn('id="copy-fallback"', CONTACT)
        self.assertIn('id="prepared-inquiry"', CONTACT)
        self.assertIn('id="copy-inquiry"', CONTACT)
        self.assertIn('<span class="required_text">Required</span>', CONTACT)
        self.assertIn('<a class="nav_contact" href="index.html">Main</a>', CONTACT)
        self.assertNotIn('aria-required="true"', CONTACT)
        self.assertNotIn('<div class="contact_expectations" aria-label=', CONTACT)

    def test_contact_handoff_is_local_bounded_and_explicit(self):
        self.assertTrue(CONTACT_SCRIPT)
        self.assertIn("operations@coppercanyonconcepts.com", CONTACT_SCRIPT)
        self.assertIn("encodeURIComponent", CONTACT_SCRIPT)
        self.assertIn("mailto:", CONTACT_SCRIPT)
        self.assertNotIn("fetch(", CONTACT_SCRIPT)
        self.assertNotIn("innerHTML", CONTACT_SCRIPT)
        self.assertIn('submitButton.disabled = false', CONTACT_SCRIPT)
        self.assertIn("MAX_MAILTO_LENGTH = 1900", CONTACT_SCRIPT)
        self.assertIn("copyText.value = preparedText", CONTACT_SCRIPT)
        self.assertIn("navigator.clipboard", CONTACT_SCRIPT)
        self.assertIn("opens your email app", CONTACT)
        self.assertIn("Do not include passwords", CONTACT)

    def test_privacy_policy_explains_contact_form_email_handoff(self):
        self.assertIn("contact form", PRIVACY)
        self.assertIn("does not send form entries to a third party form processor", PRIVACY)
        self.assertIn("remains in your browser until you choose to open your email application", PRIVACY)

    def test_contact_buttons_and_controls_use_accessible_contrast_tokens(self):
        self.assertIn("--control_line: #747474;", STYLES)
        self.assertIn(
            ".button.primary {\n  background: var(--copper_dark);",
            STYLES,
        )
        self.assertIn(
            ".button.primary:hover {\n  background: #8f3d24;",
            STYLES,
        )
        self.assertIn("border: 1px solid var(--control_line);", STYLES)
        self.assertNotIn("border: 1px solid rgba(23, 32, 38, 0.3);", STYLES)
        self.assertIn(
            ".contact_page .eyebrow,\n.contact_page .section_label {\n  color: var(--copper_dark);",
            STYLES,
        )
        self.assertIn("outline: 3px solid var(--copper_dark);", STYLES)
        self.assertIn("outline: 3px solid #fff;", STYLES)
        self.assertIn("box-shadow: 0 0 0 6px #8f3d24;", STYLES)
        self.assertGreaterEqual(contrast_ratio("#a94f2f", "#f7f3ec"), 4.5)
        self.assertGreaterEqual(contrast_ratio("#747474", "#ffffff"), 3)
        self.assertGreaterEqual(contrast_ratio("#8f3d24", "#f7f3ec"), 3)
        self.assertGreaterEqual(contrast_ratio("#ffffff", "#101a22"), 3)


if __name__ == "__main__":
    unittest.main()
