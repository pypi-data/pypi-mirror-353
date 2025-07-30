import unittest
from terminological_ontological_coverage.keyword_comparison import (
    generate_keywords_rake, generate_keywords_keybert,
    weighted_keywords_in_ontology, analyze_keywords_from_text,
    analyze_custom_keywords, load_ontology)


class TestPackage(unittest.TestCase):

    def setUp(self):
        self.text = "Water quality in the river basin is monitored."
        self.ontology_path = "doce.ttl"
        self.custom_keywords_scores = {
            "water": 0.0625,
            "Member States": 0.0525,
            "surface water": 0.0475
        }

    def test_generate_keywords_rake(self):
        keywords = generate_keywords_rake(self.text)
        self.assertIn(("0.0625", "water"), keywords)

    def test_generate_keywords_keybert(self):
        keywords = generate_keywords_keybert(self.text)
        self.assertTrue(any(keyword == "water" for score, keyword in keywords))

    def test_weighted_keywords_in_ontology(self):
        ontology = load_ontology(self.ontology_path)
        keywords_with_scores = [("0.0625", "water")]
        result = weighted_keywords_in_ontology(keywords_with_scores, ontology)
        self.assertGreater(result["weighted_percentage"], 0)

    def test_analyze_keywords_from_text(self):
        result = analyze_keywords_from_text(self.text, self.ontology_path, generate_keywords_rake)
        self.assertGreater(result["weighted_percentage"], 0)

    def test_analyze_custom_keywords(self):
        result = analyze_custom_keywords(self.custom_keywords_scores, self.ontology_path)
        self.assertGreater(result["weighted_percentage"], 0)


if __name__ == "__main__":
    unittest.main()
