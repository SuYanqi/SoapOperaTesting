from pathlib import Path

from tqdm import tqdm

from bug_automating.pipelines.evaluator import Deduplicator, Filter
from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.llm_util import LLMUtil
from config import (DATA_DIR, APP_NAME_WORDPRESS, APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, OUTPUT_DIR,
                    APP_NAME_AMAZE, APP_NAME_MARKOR, APP_NAME_DUCKGO, APP_NAME_NEWPIPE, APP_NAME_MATERIALFILES)

if __name__ == "__main__":
    # app = APP_NAME_FIREFOX
    # app = APP_NAME_ANTENNAPOD
    # app = APP_NAME_WORDPRESS
    # app = APP_NAME_AMAZE
    # app = APP_NAME_DUCKGO
    # app = APP_NAME_MARKOR
    # app = APP_NAME_NEWPIPE
    app = APP_NAME_MATERIALFILES

    with_kb = True
    # with_kb = False
    with_oracles = True
    # with_oracles = False

    Filter.filter_bugs(app, with_kb, with_oracles)
