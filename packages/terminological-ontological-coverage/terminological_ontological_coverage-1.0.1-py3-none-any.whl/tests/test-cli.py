import unittest
import subprocess
import os

class TestCLI(unittest.TestCase):

    def setUp(self):
        self.text_file_path = "normativaacque.txt"
        self.ontology_paths = ["doce.ttl", "saref4watr.ttl", "sparql_2024-04-30_15-09-23Z.ttl"]
        self.output_comparison_csv = "comparison_results.csv"
        self.output_matches_csv = "matches_results.csv"
        self.custom_keywords_file = "custom_keywords.csv"
        self.keyword_scores = {
            'water': 0.0625,
            'Member States': 0.0525,
            'surface water': 0.0475,
            'groundwater': 0.0425,
            'river basin': 0.0375,
            'status': 0.0325,
            'quality': 0.0325,
            'monitoring': 0.0325,
            'ecological': 0.0275,
            'chemical': 0.0275,
            'programme': 0.0225,
            'objectives': 0.0225,
            'measures': 0.0225,
            'pollution': 0.0225,
            'directive': 0.0225,
            'environment': 0.0175,
            'protection': 0.0175,
            'management': 0.0175,
            'community': 0.0175,
            'substances': 0.0175
        }
        self.create_custom_keywords_file()

    def create_custom_keywords_file(self):
        with open(self.custom_keywords_file, "w") as f:
            f.write("Keyword,Score\n")
            for keyword, score in self.keyword_scores.items():
                f.write(f"{keyword},{score}\n")

    def test_cli_execution(self):
        command = [
            "python", "terminological-ontological-coverage/keyword-comparison.py", self.text_file_path, *self.ontology_paths,
            self.output_comparison_csv, self.output_matches_csv,
            "--use_rake", "--use_keybert", f"--custom_keywords_file={self.custom_keywords_file}"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        self.assertIn("highest score", result.stdout)

    def tearDown(self):
        files = [self.output_comparison_csv, self.output_matches_csv, self.custom_keywords_file]
        for file in files:
            if os.path.exists(file):
                os.remove(file)


if __name__ == "__main__":
    unittest.main()
