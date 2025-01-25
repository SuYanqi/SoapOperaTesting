import asyncio
import os
from pathlib import Path

from tqdm import tqdm

from bug_automating.utils.crawel_util import CrawelUtil
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.list_util import ListUtil
from config import DATA_DIR, SYNC_CRAWEL_NUM

if __name__ == "__main__":
    """
    crawel all bug reports (with comments, history and attachments) by the bug_ids.txt
    """
    relink_index = 0
    product = "firefox"
    component = None
    start_index = 0
    end_index = None

    test_flag = True

    api_key = "aIE0knIYYAuzff5sOiD6PGT4mZZZOEg1NF9G0USu"
    params = {"api_key": api_key}
    bugs_filename = f'bugs_{start_index}_{end_index}'
    bug_ids_filename = "bug_ids"
    if test_flag:
        bugs_filename = f"test_{bugs_filename}"
        bug_ids_filename = f"test_{bug_ids_filename}"

    save_foldername = Path(DATA_DIR, product)
    if component:
        save_foldername = Path(save_foldername, f'{component}')

    if not os.path.exists(Path(save_foldername, bugs_filename)):
        # If it doesn't exist, create it
        os.makedirs(Path(save_foldername, bugs_filename))

    bug_ids = FileUtil.load_txt(Path(save_foldername, f'{bug_ids_filename}.txt'))

    # remove space
    bug_ids = [int(x.strip()) for x in bug_ids]
    bug_ids.sort(reverse=True)
    print(f"all bug id: {len(bug_ids)}")
    print(bug_ids)
    bug_ids = bug_ids[start_index:end_index]
    print(f"start bug id: {bug_ids[0]}")
    print(f"end bug id: {bug_ids[-1]}")
    print(f"bug id: {len(bug_ids)}")
    print(bug_ids)
    bug_report_urls = CrawelUtil.get_bug_report_urls(bug_ids)
    bug_comments_urls = CrawelUtil.get_bug_comments_urls(bug_ids)
    bug_history_urls = CrawelUtil.get_bug_history_urls(bug_ids)
    bug_attachments_urls = CrawelUtil.get_bug_attachments_urls(bug_ids)

    bug_report_urls_list = ListUtil.list_of_groups(bug_report_urls, SYNC_CRAWEL_NUM)
    bug_comments_urls_list = ListUtil.list_of_groups(bug_comments_urls, SYNC_CRAWEL_NUM)
    bug_history_urls_list = ListUtil.list_of_groups(bug_history_urls, SYNC_CRAWEL_NUM)
    bug_attachments_urls_list = ListUtil.list_of_groups(bug_attachments_urls, SYNC_CRAWEL_NUM)

    loop = asyncio.get_event_loop()

    for index, bug_report_urls in tqdm(enumerate(bug_report_urls_list[relink_index:]), ascii=True):
        bug_dicts = []
        bug_responses = loop.run_until_complete(CrawelUtil.crawel_by_async(bug_report_urls, params))
        bug_comments_responses = loop.run_until_complete(CrawelUtil.crawel_by_async(bug_comments_urls_list[index], params))
        bug_history_responses = loop.run_until_complete(CrawelUtil.crawel_by_async(bug_history_urls_list[index], params))
        bug_attachments_responses = loop.run_until_complete(CrawelUtil.crawel_by_async(bug_attachments_urls_list[index], params))

        for bug_response in bug_responses:
            # print(bug_response)
            try:
                bug_dict = bug_response["bugs"][0]
                for bug_comments_response in bug_comments_responses:
                    # print(bug_comments_response)
                    bug_comments_dict = bug_comments_response["bugs"]
                    if str(bug_dict['id']) in bug_comments_dict.keys():
                        # print(bug_dict['id'])
                        bug_dict["comments"] = bug_comments_dict[str(bug_dict['id'])]["comments"]
                        # print(bug_dict["comments"])
                        break
                for bug_history_response in bug_history_responses:
                    bug_history_dict = bug_history_response["bugs"]
                    if bug_history_dict[0]['id'] == bug_dict['id']:
                        # print(bug_history_dict[0]['history'])
                        bug_dict["history"] = bug_history_dict[0]['history']
                        break
                for bug_attachments_response in bug_attachments_responses:
                    # print(bug_attachments_response)
                    bug_attachments_dict = bug_attachments_response["bugs"]
                    if str(bug_dict['id']) in bug_attachments_dict.keys():
                        # print(bug_dict['id'])
                        for bug_attachment in bug_attachments_dict[str(bug_dict['id'])]:
                            bug_attachment['data'] = None
                        bug_dict["attachments"] = bug_attachments_dict[str(bug_dict['id'])]
                        break
                bug_dicts.append(bug_dict)
            except:
                continue
        FileUtil.dump_json(Path(save_foldername, bugs_filename, f'{bugs_filename}_{index+relink_index}.json'), bug_dicts)


