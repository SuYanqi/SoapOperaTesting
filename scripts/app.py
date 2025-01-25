import logging
from pathlib import Path

from tqdm import tqdm

from bug_automating.pipelines.app import App
from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.llm_util import LLMUtil
from bug_automating.utils.path_util import PathUtil
from config import APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, APP_NAME_WORDPRESS, OUTPUT_DIR

if __name__ == "__main__":

    # app_keyword = APP_NAME_FIREFOX
    # app_keyword = APP_NAME_ANTENNAPOD
    app_keyword = APP_NAME_WORDPRESS

    # planner without KB and without oracles
    with_planner_knowledge_base = False
    with_oracles = True

    # planner with KB and without oracles
    # with_planner_knowledge_base = True
    # with_oracles = False

    # planner without KB and with oracles
    # with_planner_knowledge_base = False
    # with_oracles = True

    soap_opera_test_no = 0

    bugs = FileUtil.load_pickle(PathUtil.get_bugs_filepath(app_keyword))

    soap_opera_test_list = FileUtil.load_json(Path(OUTPUT_DIR, f"{app_keyword}_soap_opera_tests.json"))

    steps = soap_opera_test_list[soap_opera_test_no]
    # for steps in tqdm(soap_opera_test_list, ascii=True):
    App.process(
        steps, bugs, app_keyword,
        # planner settings ############
        planner_model=LLMUtil.GPT4O_MODEL_NAME_WITH_DATE_08,
        planner_temperature=1,
        with_planner_cots=True,
        with_planner_instances=False,
        with_planner_format_verifier=True,
        with_knowledge_base=with_planner_knowledge_base,
        # player settings ############
        player_model=LLMUtil.GPT4O_MODEL_NAME_WITH_DATE_08,
        player_temperature=1,
        with_player_cots=True,
        with_player_instances=False,
        with_player_messages=True,
        with_player_history=True,
        with_player_original_gui=False,
        # finder settings ############
        finder_model=LLMUtil.GPT4O_MODEL_NAME_WITH_DATE_08,
        finder_temperature=1,
        with_finder_cots=True,
        with_finder_instances=False,
        with_oracles=with_oracles,
        with_finder_format_verifier=True,
        # detector settings ############
        verifier_model=LLMUtil.GPT4O_MODEL_NAME_WITH_DATE_08,
        verifier_temperature=1,
        with_verifier_cots=True,
        with_verifier_instances=False,
        with_verifier_messages=True,
        with_verifier_original_gui=True, )

