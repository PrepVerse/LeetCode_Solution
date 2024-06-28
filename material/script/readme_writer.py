import collections
import glob
import json
import requests
from requests.sessions import Session
from schema.metadata import Metadata

BADGE_PREFIX = '<img src="https://custom-icon-badges.demolab.com/badge/'
BADGE_SUFFIX = '.svg?style=plastic&logo=leetcode" />\n'


class ReadmeWriter:
  def __init__(self):
    self.session: Session = requests.Session()
    # json_data = json.loads(self.session.get("https://leetcode.com/api/problems/all", timeout=10).content.decode("utf-8"))
    # self.metadata = Metadata.from_dict(json_data)
    # self.stat_status_pairs = self.metadata.stat_status_pairs
    # self.stat_status_pairs.sort(key=lambda x: x.stat.frontend_question_id)
    # self.sols_path = "docs/solutions/"
    
    try:
        response = self.session.get("https://leetcode.com/api/problems/all", timeout=10).content.decode("utf-8")
        # response.raise_for_status()  # Raise an error for bad status codes
        print("Response content:", response[:250])
        json_data = response.json()  # Use the built-in JSON decoder
        print("JSON Data:", json.dumps(json_data, indent=2))  # Pretty-print the JSON data
        self.metadata = Metadata.from_dict(json_data)
        self.stat_status_pairs = self.metadata.stat_status_pairs
        self.stat_status_pairs.sort(key=lambda x: x.stat.frontend_question_id)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        self.metadata = None
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        self.metadata = None

    self.sols_path = "docs/solutions/"

  def write_readme(self) -> None:
    # if not self.metadata:
    #     print("Metadata is not available.")
    #     return
    num_total: int = self.metadata.num_total
    prob_count = collections.Counter()  # {int (level): int}
    ac_count = collections.Counter()  # {int (level): int}

    i=0  # Initialize i outside the loop

    for stat_status_pair in self.stat_status_pairs:
      # 1 := easy, 2 := medium, 3 := hard
      level: int = stat_status_pair.difficulty.level
      prob_count[level] += 1
      frontend_question_id: int = stat_status_pair.stat.frontend_question_id
      filled_question_id = str(frontend_question_id).zfill(4)
      matches = glob.glob(f"{self.sols_path}{filled_question_id}*")
      if matches:
        ac_count[level] += 1

    num_solved = sum(ac_count.values())

    solved_percentage: float = round((num_solved / num_total) * 100, 2)
    solved_badge: str = f"{BADGE_PREFIX}Solved-{num_solved}/{num_total}%20=%20{solved_percentage}%25-blue{BADGE_SUFFIX}"
    easy_badge: str = f"{BADGE_PREFIX}Easy-{ac_count[1]}/{prob_count[1]}-5CB85D{BADGE_SUFFIX}"
    medium_badge: str = f"{BADGE_PREFIX}Medium-{ac_count[2]}/{prob_count[2]}-F0AE4E{BADGE_SUFFIX}"
    hard_badge: str = f"{BADGE_PREFIX}Hard-{ac_count[3]}/{prob_count[3]}-D95450{BADGE_SUFFIX}"

    # Write to README
    with open("README.md", "r") as f:
      original_readme = f.readlines()

    # Find the line with solved badge and replace the following 4 lines
    for i, line in enumerate(original_readme):
      if line.startswith('<img src="https://img.shields.io/badge/Solved'):
        break
    if i < len(original_readme) - 4:
      original_readme[i] = solved_badge
      original_readme[i + 2] = easy_badge
      original_readme[i + 3] = medium_badge
      original_readme[i + 4] = hard_badge

    with open("README.md", "w+") as f:
      for line in original_readme:
        f.write(line)
