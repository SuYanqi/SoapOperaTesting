from pathlib import Path

from tqdm import tqdm

from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from config import DATA_DIR, APP_NAME_WORDPRESS, APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, OUTPUT_DIR

import random


def generate_unique_samples(range_min, range_max, sample_size):
    """
    Generates a list of unique random integer samples from a given range.

    Parameters:
    range_min (int): The minimum bound for sampling range.
    range_max (int): The maximum bound for sampling range.
    sample_size (int): The number of unique samples to generate.

    Returns:
    list: A list containing the generated unique integer samples.
    """
    if sample_size > (range_max - range_min + 1):
        raise ValueError("Sample size is larger than the available range.")

    return random.sample(range(range_min, range_max + 1), sample_size)


if __name__ == "__main__":
    # app = APP_NAME_FIREFOX
    # app = APP_NAME_ANTENNAPOD
    # app = APP_NAME_WORDPRESS
    apps = [APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, APP_NAME_WORDPRESS]
    sample_size = 100
    foldername = 'all'

    # plan_outputs = []
    # player_outputs = []
    all_outputs = []
    # all_outputs = []

    for app in apps:
        filepath = Path(OUTPUT_DIR, app, foldername)
        print(filepath)
        json_filenames = FileUtil.find_files_by_extension(filepath, 'json')
        print(json_filenames)
        json_filenames = sorted(json_filenames)
        print(json_filenames)
        print(len(json_filenames))

        output_results = []
        for json_filename in tqdm(json_filenames, ascii=True):
            # print(sec_filename)
            output_result = FileUtil.load_json(json_filename)
            output_results.append(output_result)
        print(len(output_results))

        # plan_outputs = []
        # player_outputs = []
        for output_result in output_results:
            # print(output_result)
            for one_output in output_result[Placeholder.OUTPUT_LIST]:
                try:
                    plan_output = one_output[Placeholder.PLANNER_OUTPUT]
                    player_output = one_output[Placeholder.PLAYER_OUTPUT]
                    if plan_output and player_output:
                        all_outputs.append(one_output)
                        # print(plan_output)
                        # plan_output_pair = {
                        #     'original': one_output,
                        #     'plan_output': plan_output
                        # }
                        # plan_outputs.append(plan_output_pair)
                    # player_output = one_output[Placeholder.PLAYER_OUTPUT]
                    # if player_output:
                    #     player_output_pair = {
                    #         'original': one_output,
                    #         'player_output': player_output
                    #     }
                    #     player_outputs.append(player_output_pair)
                except:
                    print(one_output)
    # print(len(plan_outputs))
    print(len(all_outputs))
    # print(len(player_outputs))
    # FileUtil.dump_json(Path(filepath, f"bug_id_{step_foldername}_ans_pairs.json"), output_results)
    # FileUtil.dump_json(Path(DATA_DIR, "section", "rest", "bug_id_ans_pairs.json"), sec_results)
    sample_nums = generate_unique_samples(0, len(all_outputs), sample_size)
    print(len(sample_nums))
    sample_outputs = []
    # sample_plan_outputs = []
    # sample_play_outputs = []
    for sample_num in sample_nums:
        sample_outputs.append(all_outputs[sample_num])
    #     sample_play_outputs.append(player_outputs[sample_num])
    # print(len(sample_plan_outputs))
    # print(len(sample_play_outputs))
    print(len(sample_outputs))
    FileUtil.dump_json(Path(OUTPUT_DIR, f'sample_outputs_{foldername}_{sample_size}.json'), sample_outputs)

    # FileUtil.dump_json(Path(OUTPUT_DIR, f'sample_plan_outputs_{foldername}_{sample_size}.json'), sample_plan_outputs)
    # FileUtil.dump_json(Path(OUTPUT_DIR, f'sample_play_outputs_{foldername}_{sample_size}.json'), sample_play_outputs)
