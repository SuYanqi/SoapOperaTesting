from bug_automating.types.bug import Bugs
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.path_util import PathUtil
from config import TO_DICT_OMIT_ATTRIBUTES, APP_NAME_WORDPRESS

if __name__ == "__main__":
    # app = "firefox"
    # app = 'antennapod'
    app = APP_NAME_WORDPRESS

    # test_flag = True
    test_flag = False
    bugs_foldername = "bugs"
    dict_filename = 'id_scenarios_dicts'
    if test_flag:
        bugs_foldername = f"test_{bugs_foldername}"
        dict_filename = f"test_{dict_filename}"
    # without_cluster_index = True
    without_cluster_index = False
    if without_cluster_index:
        TO_DICT_OMIT_ATTRIBUTES.add("cluster_index")
        filename = f'{dict_filename}_wo_cluster_index'

    bugs = FileUtil.load_pickle(PathUtil.get_bugs_filepath(app, bugs_foldername))
    # bugs = Bugs(bugs[0:10])
    id_scenarios_dicts = bugs.convert_scenarios_to_dict()
    FileUtil.dump_json(PathUtil.get_bugs_filepath(app, dict_filename), id_scenarios_dicts)
