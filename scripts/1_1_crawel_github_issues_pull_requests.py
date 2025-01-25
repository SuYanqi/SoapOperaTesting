import asyncio
import os
from pathlib import Path

from tqdm import tqdm

from bug_automating.utils.crawel_util import CrawelUtil
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.list_util import ListUtil
from config import SYNC_CRAWEL_NUM, DATA_DIR

if __name__ == "__main__":

    # # Replace with your GitHub personal access token
    # github_token = "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"
    github_token = "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"  # mobile

    headers = {
        'Authorization': f'token {github_token}',
    }
    # headers = None

    folder_name = "issues_pulls"

    # GitHub repository information
    owner = 'wordpress-mobile'
    repo = 'WordPress-Android'
    max_issue_id = 21128
    min_issue_id = 21052

    # owner = 'mozilla-mobile'
    # repo = 'fenix'

    # owner = 'TeamNewPipe'
    # repo = 'NewPipe'

    # k9-mail
    # owner = 'thunderbird'
    # repo = 'thunderbird-android'
    # max_issue_id = 8014
    # min_issue_id = 0

    # AntennaPod
    # owner = 'AntennaPod'
    # repo = 'AntennaPod'
    # max_issue_id = 7340
    # min_issue_id = 1

    filepath = Path(DATA_DIR, repo, folder_name)
    # filepath = Path(DATA_DIR, 'github', repo, 'issues')
    # Check if the folder exists
    if not os.path.exists(filepath):
        # If it doesn't exist, create it
        os.makedirs(filepath)

    # issue_urls = CrawelUtil.get_github_issue_urls(owner, repo, max_issue_id=19175)  # WordPress
    # issue_urls = CrawelUtil.get_github_issue_urls(owner, repo, max_issue_id=28833)  # mobile
    issue_urls = CrawelUtil.get_github_issue_urls(owner, repo, max_issue_id=max_issue_id, min_issue_id=min_issue_id)

    issue_urls_list = ListUtil.list_of_groups(issue_urls, SYNC_CRAWEL_NUM)
    loop = asyncio.get_event_loop()
    for index, issue_urls in tqdm(enumerate(issue_urls_list), ascii=True):
        responses = loop.run_until_complete(CrawelUtil.crawel_by_async(issue_urls, headers))

        FileUtil.dump_json(Path(filepath, f'{folder_name}_{index}.json'), responses)
