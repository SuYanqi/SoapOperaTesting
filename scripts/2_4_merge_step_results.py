from pathlib import Path

from tqdm import tqdm

from bug_automating.utils.file_util import FileUtil
from config import DATA_DIR, APP_NAME_WORDPRESS

if __name__ == "__main__":
    # app = 'firefox'
    # app = 'antennapod'
    app = APP_NAME_WORDPRESS

    # test_flag = True
    test_flag = False
    # app = 'wordpress'
    step_foldername = "step"
    if test_flag:
        step_foldername = f"test_{step_foldername}"
    # filepath = Path(OUTPUT_DIR, "section_extraction", "zero_shot")
    filepath = Path(DATA_DIR, app)
    sec_filenames = FileUtil.get_file_names_in_directory(Path(DATA_DIR, app, step_foldername), 'json')
    # sec_filenames = FileUtil.get_file_names_in_traverse_directory(Path(DATA_DIR, app, "section"), "json")
    # sec_filenames = FileUtil.get_file_names_in_traverse_directory(Path(DATA_DIR, "section", "all"), "json")
    # sec_filenames = FileUtil.get_file_names_in_traverse_directory(Path(DATA_DIR, "section", "diff"), "json")
    # sec_filenames = FileUtil.get_file_names_in_traverse_directory(Path(DATA_DIR, "section", "rest"), "json")
    # sec_filenames = FileUtil.get_file_names_in_traverse_directory(Path(DATA_DIR, "section", "rest", "diff"), "json")
    # sec_filenames = FileUtil.get_file_names_in_traverse_directory(filepath, "json")

    print(sec_filenames)
    sec_filenames = sorted(sec_filenames)
    print(sec_filenames)

    sec_results = []
    for sec_filename in tqdm(sec_filenames, ascii=True):
        # print(sec_filename)
        tmp_sec_results = FileUtil.load_json(sec_filename)
        sec_results.extend(tmp_sec_results)
    FileUtil.dump_json(Path(filepath, f"bug_id_{step_foldername}_ans_pairs.json"), sec_results)
    # FileUtil.dump_json(Path(DATA_DIR, "section", "rest", "bug_id_ans_pairs.json"), sec_results)

