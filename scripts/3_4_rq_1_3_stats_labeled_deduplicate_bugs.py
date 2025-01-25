import json
from pathlib import Path

from tqdm import tqdm

from bug_automating.pipelines.evaluator import Deduplicator
from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.llm_util import LLMUtil
from config import DATA_DIR, APP_NAME_WORDPRESS, APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, OUTPUT_DIR

if __name__ == "__main__":
    # app = APP_NAME_FIREFOX
    app = APP_NAME_ANTENNAPOD
    # app = APP_NAME_WORDPRESS
    filename = f"{app}_deduplicate_bugs_with_mark"

    with_kb = True
    # with_kb = False
    with_oracles = True
    # with_oracles = False

    suffix = ''
    if with_kb and not with_oracles:
        suffix = suffix + '_no_oracles'
    elif not with_kb and with_oracles:
        suffix = suffix + '_no_kb'
    filename = filename + suffix

    # all_bugs = Deduplicator.get_all_bugs(app)
    deduplicator_output = FileUtil.load_json(Path(OUTPUT_DIR, f"{filename}.json"))
    all_block_num = len(deduplicator_output[Placeholder.DEDUPLICATOR_OUTPUT])
    valid_enhancement_num = 0
    invalid_enhancement_num = 0
    valid_defect_num = 0
    invalid_defect_num = 0
    for one_block in deduplicator_output[Placeholder.DEDUPLICATOR_OUTPUT]:
        if one_block[Placeholder.BUG_TYPE] == Placeholder.TYPE_ENHANCEMENT:
            if one_block[Placeholder.BUG_VALIDITY] == Placeholder.VALID:
                valid_enhancement_num = valid_enhancement_num + 1
            else:
                invalid_enhancement_num = invalid_enhancement_num + 1
        else:
            if one_block[Placeholder.BUG_VALIDITY] == Placeholder.VALID:
                valid_defect_num = valid_defect_num + 1
            else:
                invalid_defect_num = invalid_defect_num + 1
    print(f"all_block_num: {all_block_num}")
    print(f"valid_enhancement_num: {valid_enhancement_num}")
    print(f"invalid_enhancement_num: {invalid_enhancement_num}")

    print(f"valid_defect_num: {valid_defect_num}")
    print(f"invalid_defect_num: {invalid_defect_num}")

    print(f"Valid: {valid_defect_num+valid_enhancement_num}")
    print(f"accuracy: {(valid_enhancement_num+valid_defect_num)/(all_block_num)}")



