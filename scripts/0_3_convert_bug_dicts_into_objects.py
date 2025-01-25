from pathlib import Path

from tqdm import tqdm

from bug_automating.types.bug import Bugs, Bug
from bug_automating.utils.file_util import FileUtil
from config import DATA_DIR

if __name__ == "__main__":
    """
    1. convert all bug_dicts into bugs
    """
    reponame = 'firefox'
    component = None
    start_index = 0
    end_index = None
    test_flag = True
    bugs_foldername = "bugs"
    if test_flag:
        bugs_foldername = f"test_{bugs_foldername}"
    save_foldername = Path(DATA_DIR, reponame)

    bug_dicts_foldername = f'{bugs_foldername}_{start_index}_{end_index}'

    if component:
        save_foldername = Path(save_foldername, f'{component}')

    bug_dicts = FileUtil.load_json(Path(save_foldername, f"{bug_dicts_foldername}.json"))
    bugs = []
    count = 0
    for bug_dict in tqdm(bug_dicts, ascii=True):
        bug = Bug.from_dict(bug_dict)
        # print(bug)
        bugs.append(bug)
    bugs = Bugs(bugs)
    bugs.overall_bugs()
    print(f"all bugs: {len(bug_dicts)}")
    print(f"all bugs: {len(bugs)}")
    # print(count)
    # bugs = bugs.to_dict()
    # print(bugs)
    # print(type(bugs))
    # for bug in bugs:
    #     pc_pair = bug.product_component_pair
    #     pc_pair = pc_pair.to_dict()
    #     print(pc_pair)
    #     print(bug)
    #     bug = bug.to_dict()
    #     print(bug)
    #     print(type(bug))
    #     FileUtil.dump_json(Path(save_foldername, f"{bugs_foldername}_dict.json"), bug)
    #     input()
    FileUtil.dump_pickle(Path(save_foldername, f"{bugs_foldername}.json"), bugs)
