from pathlib import Path

from tqdm import tqdm

from bug_automating.utils.file_util import FileUtil
from config import DATA_DIR

if __name__ == "__main__":
    github = "github"
    reponame = 'WordPress-Android'
    # reponame = 'firefox-android'
    # reponame = 'fenix'
    # reponame = 'NewPipe'
    # AntennaPod
    # owner = 'AntennaPod'
    # reponame = 'AntennaPod'
    foldername = "issues_pulls"
    filepath = Path(DATA_DIR, reponame)
    filenames = FileUtil.get_file_names_in_directory(Path(filepath, foldername), 'json')
    filenames = sorted(filenames, key=lambda x: (len(x), x))
    issues_pull_requests = []
    for filename in tqdm(filenames, ascii=True):
        temp_issues_pull_requests = FileUtil.load_json(filename)
        issues_pull_requests.extend(temp_issues_pull_requests)
    print(len(issues_pull_requests))
    FileUtil.dump_json(Path(filepath, f"{foldername}.json"), issues_pull_requests)
