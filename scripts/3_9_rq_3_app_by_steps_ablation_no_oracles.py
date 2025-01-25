from pathlib import Path

from tqdm import tqdm

from bug_automating.pipelines.app import App
from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.pipelines.player import ActionExecutor
from bug_automating.pipelines.verifier import Verifier
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.img_util import ImageUtil
from bug_automating.utils.llm_util import LLMUtil
from config import DATA_DIR, APP_NAME_WORDPRESS, APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, OUTPUT_DIR

if __name__ == "__main__":
    app = APP_NAME_FIREFOX
    # app = APP_NAME_ANTENNAPOD
    # app = APP_NAME_WORDPRESS

    verifier_model = LLMUtil.GPT4O_MODEL_NAME_WITH_DATE_08
    verifier_temperature = 1
    with_verifier_cots = True
    with_verifier_instances = False
    with_verifier_messages = True
    with_verifier_original_gui = True
    with_oracles = False

    filepath = Path(OUTPUT_DIR, app, f"all")
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
    for output_result in tqdm(output_results[0:], ascii=True):
        # print(app_directory)
        print(output_result[Placeholder.APP_DIR])
        app_directory = output_result[Placeholder.APP_DIR].replace(str(OUTPUT_DIR), "")
        app_directory = app_directory.replace("/", "")
        print(app_directory)
        original_directory = str(Path(filepath, app_directory))
        print(original_directory)
        save_directory = FileUtil.create_directory_if_not_exists(Path(OUTPUT_DIR, app, f"ablation_no_oracles"),
                                                                 app_directory,
                                                                 with_current_time=False)
        # save_directory = Path(OUTPUT_DIR, app, f"ablation_no_oracles", app_directory)
        print(save_directory)
        # print(output_result)
        verifier_messages = None
        sub_step = None

        for exploratory_count, one_output in enumerate(output_result[Placeholder.OUTPUT_LIST]):
            screenshot_name = f"{Placeholder.SCREENSHOT}_{exploratory_count}"
            # screenshot_num = screenshot_num + 1
            image_name_with_nums = f"{screenshot_name}{Placeholder.WITH_NUMS}"
            one_output[Placeholder.SCREENSHOT] = str(Path(original_directory, f"{screenshot_name}.png"))
            one_output[Placeholder.SCREENSHOT_WITH_NUMS] = str(Path(original_directory, f"{image_name_with_nums}.png"))
            base64_image = ImageUtil.encode_image(one_output[Placeholder.SCREENSHOT])
            base64_image_with_nums = ImageUtil.encode_image(one_output[Placeholder.SCREENSHOT_WITH_NUMS])
            # base64_image, base64_image_with_nums, num_coord_dict = ActionExecutor. \
            #     capture_and_process_screenshot(original_directory, screenshot_name)
            print(f"^^^Verifier^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            if with_verifier_original_gui:
                with_verifier_original_gui = base64_image
            if not with_verifier_messages:
                verifier_messages = None
            # print(sub_step)
            # print(with_oracles)
            # print(with_verifier_instances)
            # print(with_verifier_cots)
            # print()
            verifier_output, verifier_messages = Verifier.verify(sub_step=sub_step,
                                                                 base64_image_with_nums=base64_image_with_nums,
                                                                 base64_image=with_verifier_original_gui,
                                                                 oracles=with_oracles,
                                                                 with_instances=with_verifier_instances,
                                                                 with_cots=with_verifier_cots,
                                                                 messages=verifier_messages,
                                                                 model_name=verifier_model,
                                                                 temperature=verifier_temperature, )

            one_output[Placeholder.ORACLE_FINDER_OUTPUT] = None
            one_output[Placeholder.VERIFIER_OUTPUT] = verifier_output
            sub_step = one_output[Placeholder.PLAYER_OUTPUT]
        output_result[Placeholder.APP_DIR] = save_directory
        FileUtil.dump_json(Path(save_directory, f"{Placeholder.OUTPUT}.json"), output_result)
        App.create_pdf(output_result)
