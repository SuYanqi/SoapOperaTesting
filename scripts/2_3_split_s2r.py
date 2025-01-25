import json
import os
from datetime import datetime
from pathlib import Path

import openai
from tqdm import tqdm

from bug_automating.pipelines.constructor import StepSplitter
from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.llm_util import LLMUtil
from bug_automating.utils.path_util import PathUtil
from config import DATA_DIR, APP_NAME_WORDPRESS

if __name__ == "__main__":
    openai.api_key = LLMUtil.OPENAI_API_KEY
    # reponame = 'firefox'
    # reponame = 'antennapod'
    reponame = APP_NAME_WORDPRESS

    # test_flag = True
    test_flag = False

    # reponame = 'wordpress'
    step_foldername = 'step'
    bugs_foldername = 'bugs'
    section_foldername = "section"
    if test_flag:
        step_foldername = f"test_{step_foldername}"
        bugs_foldername = f"test_{bugs_foldername}"
        section_foldername = f"test_{section_foldername}"

    with_instances = True
    # with_instances = None
    with_step_type = True
    # with_step_type = False

    # filtered_bugs = FileUtil.load_pickle(PathUtil.get_filtered_bugs_filepath())
    step_result_filepath = Path(DATA_DIR, reponame, f"{step_foldername}")
    if not os.path.exists(step_result_filepath):
        # If it doesn't exist, create it
        os.makedirs(step_result_filepath)
    # bugs = FileUtil.load_pickle(Path(DATA_DIR, reponame, f'{bugs_foldername}.json'))
    # filtered_bugs.overall_bugs()
    section_answers = FileUtil.load_json(Path(DATA_DIR, reponame, f"bug_id_{section_foldername}_ans_pairs.json"))

    bug_id_answer_pairs = []
    for index, section_answer in tqdm(enumerate(section_answers), ascii=True):
        print(index)
        print(section_answer)
        answer = None
        try:
            if section_answer["ans"][Placeholder.STEPS_TO_REPRODUCE]:
                answer, _ = StepSplitter.split_s2r(section_answer["ans"][Placeholder.STEPS_TO_REPRODUCE],
                                                   with_instances, with_step_type)
                # input()
                ans_json = json.loads(answer)
                bug_id_answer_pairs.append({"bug_id": section_answer["bug_id"], "ans": ans_json[Placeholder.STEPS]})
            else:
                bug_id_answer_pairs.append({"bug_id": section_answer["bug_id"], "ans": []})
        except Exception as e:
            print(f"{e}")
            print(answer)
            pass
        print("************************************************")
        if index % 100 == 0:
            current_datetime = datetime.now()
            FileUtil.dump_json(Path(step_result_filepath, f"bug_id_ans_pairs_{current_datetime}.json"),
                               bug_id_answer_pairs)
            bug_id_answer_pairs = []

    if bug_id_answer_pairs:
        current_datetime = datetime.now()
        FileUtil.dump_json(Path(step_result_filepath, f"bug_id_ans_pairs_{current_datetime}.json"),
                           bug_id_answer_pairs)
