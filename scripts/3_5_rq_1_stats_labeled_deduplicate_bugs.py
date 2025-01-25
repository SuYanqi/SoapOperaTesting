import json
from pathlib import Path

from tqdm import tqdm

from bug_automating.pipelines.evaluator import Deduplicator
from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.llm_util import LLMUtil
from config import DATA_DIR, APP_NAME_WORDPRESS, APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, OUTPUT_DIR

if __name__ == "__main__":
    app_names = [APP_NAME_FIREFOX, APP_NAME_WORDPRESS, APP_NAME_ANTENNAPOD]

    invalid_reason_count_dict = {}
    invalid_number = 0
    for app in app_names:
        # app = APP_NAME_FIREFOX
        # app = APP_NAME_ANTENNAPOD
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
            if one_block[Placeholder.BUG_VALIDITY] == Placeholder.INVALID:
                invalid_number = invalid_number + 1
                reason = one_block[Placeholder.VALIDITY_REASON].strip()
                invalid_reason_count_dict[reason] = \
                    invalid_reason_count_dict.get(reason, 0) + 1

        for one_block in deduplicator_output[Placeholder.DEDUPLICATOR_OUTPUT]:
            # LLMs Hallucination
            reasons = [Placeholder.INVALID_OPTION_5, Placeholder.INVALID_OPTION_7]

            # reason = Placeholder.INVALID_OPTION_5
            reason = Placeholder.INVALID_OPTION_6
            print(reason)
            if one_block[Placeholder.BUG_VALIDITY] == Placeholder.INVALID:
                if one_block[Placeholder.VALIDITY_REASON].strip() == reason:
                    # print(one_block)
                    print(json.dumps(one_block, indent=4))
                    print("#######################")

    for invalid_reason, count in invalid_reason_count_dict.items():
        print(f"{invalid_reason}: {count}")

    print(f"invalid_number: {invalid_number}")

