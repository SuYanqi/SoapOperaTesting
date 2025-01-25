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

    sample_size = 100
    foldername = 'all'

    save_filename = f"sample_outputs_{foldername}_{sample_size}_with_mark"
    sample_size = 50
    sample_outputs = FileUtil.load_json(Path(OUTPUT_DIR, f'{save_filename}.json'))
    sample_outputs = sample_outputs[0:sample_size]
    print(len(sample_outputs))

    plan_current_step_accuracy = 0
    # plan_current_step_hit = 0
    plan_sub_steps_likert = {

    }
    play_parse_acc = 0
    element_acc = 0
    for sample_output in sample_outputs:
        if sample_output[Placeholder.PLAN_CURRENT_STEP_VALIDITY] == Placeholder.VALID:
            plan_current_step_accuracy = plan_current_step_accuracy + 1
        plan_sub_steps_likert[sample_output[Placeholder.PLAN_SUB_STEPS_VALIDITY]] = plan_sub_steps_likert.get(sample_output[Placeholder.PLAN_SUB_STEPS_VALIDITY], 0) + 1
        if sample_output[Placeholder.PLAY_STEP_PARSE_VALIDITY] == Placeholder.VALID:
            play_parse_acc = play_parse_acc + 1
        if sample_output[Placeholder.PLAY_ELEMENT_LOCATION_VALIDITY] == Placeholder.VALID:
            element_acc = element_acc + 1

    print(f"Plan current step acc: {plan_current_step_accuracy/sample_size}")

    print(f"Plan sub steps likert: {plan_sub_steps_likert}")
    print(f"play_parse_acc: {play_parse_acc/sample_size}")
    print(f"element_acc: {element_acc / sample_size}")
