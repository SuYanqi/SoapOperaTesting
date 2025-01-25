import os
from pathlib import Path

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root Directory

DATA_DIR = str(Path(ROOT_DIR, "data"))

LOG_DIR = str(Path(ROOT_DIR, "log"))

OUTPUT_DIR = str(Path(ROOT_DIR, "output"))

SEED_FILTER_COUNT_THRESHOLD = 2  # SeedExtractor.filter_seeds_by_count(seed_count_dict)

ELEMENT_MERGE_THRESHOLD = 0.85

ACTION_MERGE_THRESHOLD = 0.85

STEP_CLUSTER_THRESHOLD = 0.85

SPACY_BATCH_SIZE = 1024

SBERT_BATCH_SIZE = 64

STEP_MAX_TOKEN_NUM = 64

MAX_STEP_NUM = 20

DATETIME_FORMAT = "%Y-%m-%d"

COMMIT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

COMMIT_MESSAGE_JSON_LINK = "https://hg.mozilla.org/mozilla-central/json-rev/"
COMMIT_MESSAGE_LINK = "https://hg.mozilla.org/mozilla-central/rev/"

FILE_REVISIONS_JSON_LINK = "https://hg.mozilla.org/mozilla-central/json-log/"
FILE_REVISIONS_LINK = "https://hg.mozilla.org/mozilla-central/log/"

FILE_CONTENT_JSON_LINK = "https://hg.mozilla.org/mozilla-central/json-file/"
FILE_CONTENT_LINK = "https://hg.mozilla.org/mozilla-central/file/"

FILE_ANNOTATES_JSON_LINK = "https://hg.mozilla.org/mozilla-central/json-annotate/"
FILE_ANNOTATES_LINK = "https://hg.mozilla.org/mozilla-central/annotate/"

SLEEP_TIME = 60

MAX_RETRIES = 20

SYNC_CRAWEL_NUM = 100

BUG_JSON_LINK = "https://bugzilla.mozilla.org/rest/bug/"
BUG_COMMENT = "/comment"
BUG_HISTORY = "/history"
BUG_ATTACHMENT = "/attachment"
MOZILLA_BUG_LINK = 'https://bugzilla.mozilla.org/show_bug.cgi?id='

GITHUB_ISSUE_LINK = 'https://api.github.com/repos/{owner_name}/{repo_name}/issues'
GITHUB_PULL_LINK = 'https://api.github.com/repos/{owner_name}/{repo_name}/pulls'
GITHUB_COMMIT_LINK = 'https://api.github.com/repos/{owner_name}/{repo_name}/commits'
GITHUB_COMMIT_FILE_LINK = 'https://api.github.com/repos/{owner_name}/{repo_name}/contents/{file_path}?ref={commit_oid}'
GITHUB_GRAPHQL_LINK = 'https://api.github.com/graphql'
GITHUB_ISSUES = 'issues'
GITHUB_PULL = 'pull'

MAX_EXPLORATORY_COUNT = 15
SYNC_EMBEDDING_NUM = 2000
STEP_MERGE_THRESHOLD = 0.85

TO_DICT_OMIT_ATTRIBUTES = {"prev_step", "next_step", "bug",
                           # "product_component_pair", "tossing_path",
                           # "creation_time", "closed_time", "last_change_time", "status", "labels",
                           # "relation", "keywords", "attachments",
                           # "closer_pulls", "closed_issues", "crossref_issues", "crossref_pulls", "commits"
                           }

APP_NAME_FIREFOX = "firefox"
APP_NAME_ANTENNAPOD = 'antennapod'
APP_NAME_WORDPRESS = "jetpack"

BUG_LINK_ANTENNAPOD = 'https://github.com/AntennaPod/AntennaPod/issues/'


