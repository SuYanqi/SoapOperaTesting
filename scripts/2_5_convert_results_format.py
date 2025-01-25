from pathlib import Path

from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from config import DATA_DIR, APP_NAME_WORDPRESS


def convert_result_format(sec_step_result):
    bug_id = sec_step_result['bug_id']
    ans = sec_step_result['ans']
    steps = []
    for step in ans[Placeholder.STEPS_TO_REPRODUCE]:
        if step[Placeholder.STEP_TYPE] == Placeholder.OPERATION:
            step_type = 'ACTION'
        else:
            step_type = 'CHECK'
        cluster_index = None
        # if step.is_operational:
        #     cluster_index = step.cluster_index
        step_dict = {
            'STEP': step[Placeholder.STEP],
            'STEP_TYPE': step_type,
            'CLUSTER_INDEX': cluster_index,
        }
        steps.append(step_dict)
    if ans and ans[Placeholder.EXPECTED_RESULTS]:
        for expected_result in ans[Placeholder.EXPECTED_RESULTS]:
            step_dict = {
                'STEP': expected_result,
                'STEP_TYPE': 'CHECK',
                'CLUSTER_INDEX': None,
            }
            steps.append(step_dict)

    test_scenario = {
        'SUMMARY': None,
        'PRECONDITIONS': ans[Placeholder.PRECONDITIONS],
        'STEPS': steps

    }
    # test_scenarios = []
    ans = {
        'TEST_SCENARIOS': [test_scenario]
    }
    bug_dict = {
        'bug_id': bug_id,
        'ans': ans
    }
    return bug_dict


if __name__ == "__main__":
    # app = 'firefox'
    app = APP_NAME_WORDPRESS
    # app = 'antennapod'
    # test_flag = True
    test_flag = False

    sec_foldername = "section"
    step_foldername = "step"
    if test_flag:
        sec_foldername = f"test_{sec_foldername}"
        step_foldername = f"test_{step_foldername}"
    # filepath = Path(OUTPUT_DIR, "section_extraction", "zero_shot")
    filepath = Path(DATA_DIR, app)

    sec_results = FileUtil.load_json(Path(filepath, f"bug_id_{sec_foldername}_ans_pairs.json"))
    step_results = FileUtil.load_json(Path(filepath, f"bug_id_{step_foldername}_ans_pairs.json"))
    # FileUtil.dump_json(Path(DATA_DIR, "section", "rest", "bug_id_ans_pairs.json"), sec_results)
    count = 0
    sec_step_results = []
    for sec_result in sec_results:
        bug_id = sec_result['bug_id']
        for step_result in step_results:
            step_bug_id = step_result['bug_id']
            if bug_id == step_bug_id:
                sec_result['ans'][Placeholder.STEPS_TO_REPRODUCE] = step_result['ans']
                break
        try:
            sec_result = convert_result_format(sec_result)
            sec_step_results.append(sec_result)
        except Exception as e:
            count = count + 1
            print(count)
            print(e)
            print(sec_result)
            pass
    FileUtil.dump_json(Path(filepath, f"{sec_foldername}_{step_foldername}_results.json"), sec_step_results)
