from pathlib import Path

from tqdm import tqdm

from bug_automating.utils.file_util import FileUtil
from config import DATA_DIR

if __name__ == "__main__":
    """
    merge bugs into one file
    """
    reponame = 'firefox'
    test_flag = True
    component = None
    start_index = 0
    end_index = None
    foldername = f'bugs_{start_index}_{end_index}'
    if test_flag:
        foldername = f"test_{foldername}"
    save_foldername = Path(DATA_DIR, reponame)

    if component:
        save_foldername = Path(save_foldername, f'{component}')
    save_filepath = Path(save_foldername, foldername)

    issues_pulls = FileUtil.merge_files_under_directory(save_filepath)
    print(len(issues_pulls))
    FileUtil.dump_json(Path(save_foldername, f"{foldername}.json"), issues_pulls)
