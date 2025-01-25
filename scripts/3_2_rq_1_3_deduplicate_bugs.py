from pathlib import Path

from tqdm import tqdm

from bug_automating.pipelines.evaluator import Deduplicator
from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.llm_util import LLMUtil
from config import DATA_DIR, APP_NAME_WORDPRESS, APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, OUTPUT_DIR

if __name__ == "__main__":
    # app = APP_NAME_FIREFOX
    # app = APP_NAME_ANTENNAPOD
    app = APP_NAME_WORDPRESS
    input_filename = f'{app}_classified_bugs'
    save_filename = f"{app}_deduplicate_bugs"
    # with_kb = True
    with_kb = False
    with_oracles = True
    # with_oracles = False
    suffix = ''
    if with_kb and not with_oracles:
        suffix = suffix + '_no_oracles'
    elif not with_kb and with_oracles:
        suffix = suffix + '_no_kb'
    input_filename = input_filename + suffix
    save_filename = save_filename + suffix

    # all_bugs = Deduplicator.get_all_bugs(app)
    all_bugs = FileUtil.load_json(Path(OUTPUT_DIR, f'{input_filename}.json'))
    print(f"Valid bugs in the output: {len(all_bugs[Placeholder.VALID_ISSUES])}")
    print(f"Invalid bugs in the output: {len(all_bugs[Placeholder.INVALID_ISSUES])}")
    all_bugs = all_bugs[Placeholder.VALID_ISSUES]

    print(f"All bugs as input: {len(all_bugs)}")
    deduplicator_output = Deduplicator.deduplicate_bugs_in_the_loop(all_bugs, app)
    FileUtil.dump_json(Path(OUTPUT_DIR, f"{save_filename}.json"), deduplicator_output)

    # filepath = Path(OUTPUT_DIR, app)
    # filename = f"{app}_deduplicate_bugs"
    # all_bugs = Deduplicator.get_all_bugs(app)
    # print(len(all_bugs))
    #
    # # enhancement_bugs = []
    # # defect_bugs = []
    # # other_bugs = []
    # # for bug in all_bugs:
    # #     if bug[f"{Placeholder.BUG_TYPE}"] == "Defect":
    # #         defect_bugs.append(bug)
    # #     elif bug[Placeholder.BUG_TYPE] == "Enhancement":
    # #         enhancement_bugs.append(bug)
    # #     else:
    # #         print(bug[f"{Placeholder.BUG_TYPE}"])
    # #         other_bugs.append(bug)
    # #         print(bug)
    # # print(f"enhancement_bugs: {len(enhancement_bugs)}")
    # # print(f"defect_bugs: {len(defect_bugs)}")
    # # print(f"others: {len(other_bugs)}")
    #
    # # print(len(all_bugs))
    # answer, messages, cost = Deduplicator.deduplicate(all_bugs, model=LLMUtil.GPT4O_MODEL_NAME_WITH_DATE_08,
    #                                                   temperature=0)
    # # print(answer)
    # # print(type(answer))
    # # LLMUtil.show_messages(messages)
    # # print(cost)
    # # answer = FileUtil.load_json(Path(OUTPUT_DIR, f"{filename}.json"))
    # deduplicate_bugs = Deduplicator.get_bugs_from_answer(answer)
    # print(len(deduplicate_bugs))
    #
    # output = Deduplicator.get_the_rest_bugs(answer, all_bugs)
    # deduplicate_bugs = Deduplicator.get_bugs_from_answer(output)
    # print(len(deduplicate_bugs))
    #
    # FileUtil.dump_json(Path(OUTPUT_DIR, f"{filename}.json"), output)

