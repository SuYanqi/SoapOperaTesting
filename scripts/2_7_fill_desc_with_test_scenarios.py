from pathlib import Path

from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.path_util import PathUtil
from config import DATA_DIR, APP_NAME_WORDPRESS

if __name__ == "__main__":
    # app_keyword = "firefox"
    # app_keyword = "antennapod"
    app_keyword = APP_NAME_WORDPRESS

    # test_flag = True
    test_flag = False
    bugs_foldername = "bugs"
    section_foldername = "section"
    step_foldername = "step"
    cluster_foldername = "cluster"
    if test_flag:
        bugs_foldername = f"test_{bugs_foldername}"
        section_foldername = f"test_{section_foldername}"
        step_foldername = f"test_{step_foldername}"
        cluster_foldername = f"test_{cluster_foldername}"
    foldername = f"{section_foldername}_{step_foldername}_{cluster_foldername}_results"
    bugs = FileUtil.load_pickle(PathUtil.get_bugs_filepath(app_keyword, bugs_foldername))
    step_clusterer_output = FileUtil.load_json(Path(DATA_DIR, app_keyword, f"{foldername}.json"))
    bugs.fill_desc_with_test_scenarios(step_clusterer_output)
    bugs.get_cluster_index_steps_dict()
    bugs.get_cluster_index_checkitems_dict()
    FileUtil.dump_pickle(PathUtil.get_bugs_filepath(app_keyword, bugs_foldername), bugs)

