import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path

import requests
import aiohttp
import asyncio
import json

# from bs4 import BeautifulSoup
from tqdm import tqdm

from bug_automating.utils.datetime_util import DatetimeUtil
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.nlp_util import NLPUtil
from config import DATA_DIR, COMMIT_MESSAGE_JSON_LINK, FILE_REVISIONS_JSON_LINK, MAX_RETRIES, SLEEP_TIME, BUG_JSON_LINK, \
    BUG_COMMENT, \
    BUG_HISTORY, BUG_ATTACHMENT, FILE_ANNOTATES_JSON_LINK, GITHUB_ISSUE_LINK, GITHUB_PULL_LINK, GITHUB_COMMIT_LINK, \
    GITHUB_GRAPHQL_LINK, GITHUB_COMMIT_FILE_LINK


class CrawelUtil:
    # https://bmo.readthedocs.io/en/latest/api/
    @staticmethod
    def get_specific_product_bug_ids(product):
        components = CrawelUtil.get_components_by_product(product)

        r = requests.get('https://bugzilla.mozilla.org/rest/login?login=2636370678@qq.com&password=Hanhaochun@717')
        print(r)
        print(r.text)
        url = 'https://bugzilla.mozilla.org/rest/bug'
        query_tem = "?product={}&component={}&limit={}&offset={}&include_fields=id"
        limit = 10000
        for index, component in tqdm(enumerate(components), ascii=True):
            product = product
            bug_ids = []
            for j in range(1000):
                offset = limit * j
                query_pc = query_tem.format(product, component, limit, offset)
                query_url = url + query_pc
                search_results = requests.get(query_url)
                response_data = json.loads(search_results.text)
                bugs = response_data["bugs"]
                # print(bugs)
                if len(bugs) == 0:
                    break
                for bug in bugs:
                    bug_ids.append(str(bug['id']))
            FileUtil.dump_list_to_txt(Path(DATA_DIR, f"{product}_bug_ids", f"{product}_{component}_bug_ids.txt"),
                                      bug_ids)

    @staticmethod
    def get_specific_product_component_bug_ids(product, component=None):
        bug_ids_foldername = "bug_ids"
        save_foldername = Path(DATA_DIR, product)
        if component:
            save_foldername = Path(DATA_DIR, product, component)
        if not os.path.exists(save_foldername):
            # If it doesn't exist, create it
            os.makedirs(save_foldername)
        api_key = "aIE0knIYYAuzff5sOiD6PGT4mZZZOEg1NF9G0USu"
        # r = requests.get(f'https://bugzilla.mozilla.org/rest/login?login=buglinking@gmail.com&password=suyanqi@0924/valid_login?api_key={api_key}')
        # r = requests.get(f'https://bugzilla.mozilla.org/rest/login?login=buglinking@gmail.com&password=suyanqi@0924/valid_login?api_key={api_key}')
        # print(r)
        # print(r.text)
        url = 'https://bugzilla.mozilla.org/rest/bug'
        query_tem = "?product={}&limit={}&offset={}&include_fields=id"
        if component:
            query_tem = "?product={}&component={}&limit={}&offset={}&include_fields=id"
        limit = 10000

        bug_ids = []
        for j in range(1000):
            offset = limit * j
            query_pc = query_tem.format(product, limit, offset)
            if component:
                query_pc = query_tem.format(product, component, limit, offset)
            query_url = url + query_pc
            search_results = requests.get(query_url, params={"api_key": api_key})
            response_data = json.loads(search_results.text)
            bugs = response_data["bugs"]
            # print(bugs)
            if len(bugs) == 0:
                break
            for bug in bugs:
                bug_ids.append(str(bug['id']))

        FileUtil.dump_list_to_txt(Path(save_foldername, f"{bug_ids_foldername}.txt"),
                                  bug_ids)

    # @staticmethod
    # def get_classifications(url="https://bugzilla.mozilla.org/query.cgi?format=advanced"):
    #     # Make an HTTP request to the webpage
    #     response = requests.get(url)
    #
    #     # Parse the HTML content of the webpage
    #     soup = BeautifulSoup(response.text, 'html.parser')
    #
    #     # Locate the container that holds the options
    #     options_container = soup.find('div', id='container_classification')
    #     # print(options_container)
    #     # Extract the options
    #     options = options_container.find_all('option')
    #     classifications = []
    #     # Iterate through the options and print their text
    #     for option in options:
    #         classifications.append(option.text.strip())
    #     return classifications

    @staticmethod
    def get_products_by_classification(classification_name):
        url = f'https://bugzilla.mozilla.org/rest/classification/{classification_name}'
        search_results = requests.get(url)
        response_data = json.loads(search_results.text)
        products = []
        for product in response_data["classifications"][0]["products"]:
            products.append(product["name"])
        return products

    @staticmethod
    def get_components_by_product(product_name):
        url = f'https://bugzilla.mozilla.org/rest/product/{product_name}'
        search_results = requests.get(url)
        response_data = json.loads(search_results.text)
        components = []
        for response in response_data["products"][0]["components"]:
            components.append(response['name'])
        return components

    @staticmethod
    def crawel_commit_message_ids(start_date='2022-05-01', end_date='2023-05-08'):
        """
        [start_date, end_date)
        """
        date_list = DatetimeUtil.divide_date_by_timedelta(start_date, end_date)
        commit_message_ids = []
        # l = [1,2,3,4,5,6]
        # zip(l,l[1:])
        # [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]
        for date1, date2 in zip(date_list, date_list[1:]):
            # print(date1)
            # print(date2)
            # print("#######################")
            url = f"https://hg.mozilla.org/mozilla-central/pushloghtml?" \
                  f"startdate={date1}" \
                  f"&enddate={date2}"
            while True:
                crawel_results = requests.get(url)
                if '</table>' in crawel_results.text:
                    break
                # print(type(search_results))
                # print(type(search_results.text))
            FileUtil.dump_txt(Path(DATA_DIR, "commit_messages", "raw_html_ids", f"{date1}_{date2}.txt"),
                              crawel_results.text)
            ids = CrawelUtil.get_commit_message_ids_from_html_txt(crawel_results.text)
            commit_message_ids.extend(ids)
            # print(commit_message_ids)
            # print(len(ids))
            # print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        # print(len(commit_message_ids))
        FileUtil.dump_list_to_txt(Path(DATA_DIR, "commit_messages", f"commit_messages_ids.txt"),
                                  commit_message_ids)
        return commit_message_ids

    @staticmethod
    def get_commit_message_ids_from_html_txt(html_txt):
        ids = []
        id_links = re.findall('/mozilla-central/rev/[a-zA-Z0-9]+', html_txt)
        for id_link in id_links:
            id = id_link.replace('/mozilla-central/rev/', '')
            ids.append(id)
        return ids

    @staticmethod
    def crawel_commit_messages_from_ids(commit_message_ids):
        for commit_message_id in commit_message_ids:
            commit_message_link = f"{COMMIT_MESSAGE_JSON_LINK}{commit_message_id}"
            search_results = requests.get(commit_message_link)
            # print(search_results)
            # print(search_results.text)
            # print("\nok\n\n")
            response_data = json.loads(search_results.text)
            print(response_data)

    @staticmethod
    def crawel_commit_message_from_id(commit_message_id, session=None):
        if session is None:
            session = requests.Session()
        commit_message_link = f"{COMMIT_MESSAGE_JSON_LINK}{commit_message_id}"
        # print(commit_message_link)

        headers = {'Accept-Encoding': 'gzip'}
        search_results = session.get(commit_message_link, headers=headers)
        # print(search_results)
        # print(search_results.text)
        # print("\nok\n\n")
        commit_message = search_results.json()
        # commit_message = json.loads(search_results.text)
        # get file's revisions
        for file_dict in commit_message['files']:
            file_name = file_dict['file']
            file_dict['revisions'] = CrawelUtil.crawel_file_revisions(commit_message_id, file_name, session)
        return commit_message

    @staticmethod
    def crawel_file_revisions(commit_message_id, file_name, session=None):
        if session is None:
            session = requests.Session()
        file_revisions_link = f"{FILE_REVISIONS_JSON_LINK}{commit_message_id}/{file_name}"
        # print(file_revisions_link)
        headers = {'Accept-Encoding': 'gzip'}
        search_results = session.get(file_revisions_link, headers=headers)
        # print(search_results)
        # print(search_results.text)
        # print("\nok\n\n")
        file_revisions = search_results.json()
        # file_revisions = json.loads(file_revisions.text)
        return file_revisions

    @staticmethod
    def get_commit_message_urls(commit_message_ids):
        urls = []
        for commit_message_id in tqdm(commit_message_ids, ascii=True):
            commit_message_link = f"{COMMIT_MESSAGE_JSON_LINK}{commit_message_id}"
            urls.append(commit_message_link)
        return urls

    @staticmethod
    def get_bug_report_urls(bug_report_ids):
        urls = []
        for bug_report_id in tqdm(bug_report_ids, ascii=True):
            bug_report_link = f"{BUG_JSON_LINK}{bug_report_id}"
            urls.append(bug_report_link)
        return urls

    @staticmethod
    def get_bug_comments_urls(bug_report_ids):
        urls = []
        for bug_report_id in tqdm(bug_report_ids, ascii=True):
            bug_comment_link = f"{BUG_JSON_LINK}{bug_report_id}{BUG_COMMENT}"
            urls.append(bug_comment_link)
        return urls

    @staticmethod
    def get_bug_history_urls(bug_report_ids):
        urls = []
        for bug_report_id in tqdm(bug_report_ids, ascii=True):
            bug_history_link = f"{BUG_JSON_LINK}{bug_report_id}{BUG_HISTORY}"
            urls.append(bug_history_link)
        return urls

    @staticmethod
    def get_bug_attachments_urls(bug_report_ids):
        urls = []
        for bug_report_id in bug_report_ids:
            bug_attachment_link = f"{BUG_JSON_LINK}{bug_report_id}{BUG_ATTACHMENT}"
            urls.append(bug_attachment_link)
        return urls

    @staticmethod
    def get_revisions_urls(commit_message):
        urls = []
        for file in commit_message['files']:
            file_revisions_link = f"{FILE_REVISIONS_JSON_LINK}{commit_message['node']}/{file['file']}"
            urls.append(file_revisions_link)
        return urls

    @staticmethod
    def get_annotates_urls(commit_message):
        urls = []
        for file in commit_message['files']:
            file_revisions_link = f"{FILE_ANNOTATES_JSON_LINK}{commit_message['node']}/{file['file']}"
            urls.append(file_revisions_link)
        return urls

    # ********************sync*********************
    @staticmethod
    async def fetch_multiple(urls, retry_count=0, headers=None):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')
        # while True:
        try:
            async with aiohttp.ClientSession() as session:
                tasks = [CrawelUtil.fetch(session, url, headers=headers) for url in urls]
                responses = await asyncio.gather(*tasks)
            return responses
        except Exception as e:
            if retry_count == MAX_RETRIES:
                raise e
            # logging.info(f"{retry_count}: sleeping...")
            # retry_count = retry_count + 1
            await asyncio.sleep(1)
            return await CrawelUtil.fetch_multiple(urls, retry_count + 1, headers=headers)

    # @staticmethod
    # async def fetch(session, url, retry_count=0, headers=None):
    #     logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
    #                         level=logging.INFO,
    #                         datefmt='%Y-%m-%d %H:%M:%S')
    #     # while True:
    #     try:
    #         async with session.get(url, headers=headers) as response:
    #             # if response.status == 200:
    #             return await response.json()
    #             # else:
    #             #     print(f'Error: {response.status}')
    #             #     await asyncio.sleep(1)
    #             #     return await CrawelUtil.fetch(session, url, retry_count + 1, headers)
    #     except Exception as e:
    #         if retry_count == MAX_RETRIES:
    #             raise e
    #         # logging.info(f"{retry_count}: sleeping...")
    #         # retry_count = retry_count + 1
    #         await asyncio.sleep(1)
    #         return await CrawelUtil.fetch(session, url, retry_count + 1, headers)

    @staticmethod
    def check_github_api_rate_limit():
        github_token = "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"

        username = 'wordpress-mobile'
        reponame = 'WordPress-Android'
        # issuenum = 19150
        issuenum = 19154

        # URL for the GitHub REST API to fetch the commit.
        api_url = f"https://api.github.com/repos/{username}/{reponame}/issues/{issuenum}"

        # Set up headers with your access token.
        headers = {
            "Authorization": f"token {github_token}",
        }

        # Send a GET request to fetch the commit.
        response = requests.get(api_url, headers=headers)
        return response

    @staticmethod
    async def fetch(session, url, retry_count=0, headers=None):
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            datefmt='%Y-%m-%d %H:%M:%S')

        # while True:
        try:
            if not NLPUtil.is_url(url):
                # print(url)
                response = await session.post(GITHUB_GRAPHQL_LINK, headers=headers, json={"query": url})
                # print(response)
                # check_response = CrawelUtil.check_github_api_rate_limit()
                # print(check_response.status)
                # if check_response.status == 403:
                #     response = check_response
            else:
                response = await session.get(url, headers=headers)
                # print(response.json())
                # print(response.headers.get("X-RateLimit-Used"))
            async with response:
                # print(response.status)
            # async with session.get(url, headers=headers) as response:
                rate_limit_used = int(response.headers.get("X-RateLimit-Used", 0))
                rate_limit_limit = int(response.headers.get("X-RateLimit-Limit", 1))
                if rate_limit_used < rate_limit_limit:
                    if response.status != 200:
                        print(f"Error: {response.status}: {response.json()}")
                        return await response.json()
                    return await response.json()
                else:
                    print("Rate limit exceeded. Waiting for recovery...")
                    # Parse the 'X-RateLimit-Reset' header to determine when the rate limit will reset.
                    reset_timestamp = int(response.headers.get("X-RateLimit-Reset", time.time()))
                    current_timestamp = time.time()
                    wait_time = max(reset_timestamp - current_timestamp, 1)  # Wait at least 1 second.
                    # Get the current date and time.
                    current_time = datetime.now()
                    # Extract hours, minutes, and seconds.
                    current_hour = current_time.hour
                    current_minute = current_time.minute
                    current_second = current_time.second
                    # Display the current time.
                    print(f"Current Time: {current_hour:02d}:{current_minute:02d}:{current_second:02d}")
                    # print(f"current_timestamp: {current_timestamp}")
                    print("Remaining time until rate limit resets:", wait_time, "seconds equal to",
                          wait_time / 60.0, "mins")

                    # print(f"wait_time: {wait_time} seconds")
                    await asyncio.sleep(wait_time)
                    return await CrawelUtil.fetch(session, url, retry_count + 1, headers)

                # if response.status == 200:
                #     return await response.json()
                # elif response.status == 403:
                #     print("Rate limit exceeded. Waiting for recovery...")
                #     # Parse the 'X-RateLimit-Reset' header to determine when the rate limit will reset.
                #     reset_timestamp = int(response.headers.get("X-RateLimit-Reset", time.time()))
                #     current_timestamp = time.time()
                #     wait_time = max(reset_timestamp - current_timestamp, 1)  # Wait at least 1 second.
                #     # Get the current date and time.
                #     current_time = datetime.now()
                #     # Extract hours, minutes, and seconds.
                #     current_hour = current_time.hour
                #     current_minute = current_time.minute
                #     current_second = current_time.second
                #     # Display the current time.
                #     print(f"Current Time: {current_hour:02d}:{current_minute:02d}:{current_second:02d}")
                #     # print(f"current_timestamp: {current_timestamp}")
                #     print("Remaining time until rate limit resets:", wait_time, "seconds equal to",
                #           wait_time / 60.0, "mins")
                #
                #     # print(f"wait_time: {wait_time} seconds")
                #     await asyncio.sleep(wait_time)
                #     return await CrawelUtil.fetch(session, url, retry_count + 1, headers)
                # else:
                #     print(f"Error: {response.status}: {response.json()}")
                #     return await response.json()
        except Exception as e:
            if retry_count == MAX_RETRIES:
                raise e
            # logging.info(f"{retry_count}: sleeping...")
            # retry_count = retry_count + 1
            await asyncio.sleep(1)
            return await CrawelUtil.fetch(session, url, retry_count + 1, headers)

    @staticmethod
    async def crawel_by_async(urls, headers=None):
        # urls = ['https://hg.mozilla.org/mozilla-central/json-rev/a878a69335a2b51b5613687777fd843b25a7215e',
        #         'https://hg.mozilla.org/mozilla-central/json-rev/e94e0e699e55cecd6110551f918c46cb9fa90a82',
        #         'https://hg.mozilla.org/mozilla-central/json-rev/1b0ce2a20f13235cae99937cd749acfcdaa80665',
        #         'https://hg.mozilla.org/mozilla-central/json-rev/e5627209199d609d94384bdc05eb1c3a7c83515e',
        #         'https://hg.mozilla.org/mozilla-central/json-rev/8121bf2bc0ebbab5033e98fe29a588072a106d49',
        #         'https://hg.mozilla.org/mozilla-central/json-rev/95ea47320859cfbbc9afaefbce8bceecf19149d3',
        #         'https://hg.mozilla.org/mozilla-central/json-rev/39527ef2a476787b50772c1b3c616e352d75da1d',
        #         'https://hg.mozilla.org/mozilla-central/json-rev/7a7919026510de3f91c6c143f4e302943f43404d',
        #         'https://hg.mozilla.org/mozilla-central/json-rev/0a736f3ff23c29fa14e82a769aa32e2314641c08',
        #         'https://hg.mozilla.org/mozilla-central/json-rev/2943c62bd7a2ed5bec69deaea1bb43ca63b510d4']
        # responses = await CrawelUtil.fetch_multiple(urls)
        # FileUtil.dump_json(Path(DATA_DIR, 'commit_messages', 'commit_messages',
        #                         f'commit_messages_{index}.json'), responses)

        responses = await CrawelUtil.fetch_multiple(urls, headers=headers)
        return responses

    # get urls for github
    @staticmethod
    def get_github_issue_urls(owner_name, repo_name, max_issue_id, min_issue_id=0):
        issue_link = GITHUB_ISSUE_LINK.format(owner_name=owner_name, repo_name=repo_name)
        issue_links = []
        for i in range(max_issue_id, min_issue_id, -1):
            new_issue_link = issue_link + f'/{i}'
            issue_links.append(new_issue_link)
        return issue_links

    @staticmethod
    def get_github_issue_or_pull_request_nums(issue_or_pull_requests):
        numbers = []
        for issue_or_pull_request in issue_or_pull_requests:
            # print(issue_or_pull_request)
            try:
                numbers.append(issue_or_pull_request["number"])
            except:
                pass
        return numbers

    @staticmethod
    def get_github_commits_urls_by_pull_request_nums(owner_name, repo_name, pull_request_nums):
        pull_link = GITHUB_PULL_LINK.format(owner_name=owner_name, repo_name=repo_name)
        commits_links = []
        for pull_request_num in pull_request_nums:
            commits_link = pull_link + f'/{pull_request_num}/commits'
            commits_links.append(commits_link)
        return commits_links

    @staticmethod
    def get_github_commit_shas_from_commits_links(commits_urls):
        commit_shas = []
        for commits_url in tqdm(commits_urls):
            for commit_url in commits_url:
                commit_shas.append(commit_url["sha"])
        return commit_shas

    @staticmethod
    def get_github_commit_shas_from_commit_file_blames(commit_file_blames):
        commit_shas = set()
        for commit_file_blame in tqdm(commit_file_blames, ascii=True):
            try:
                blame_ranges = commit_file_blame['blame']['ranges']
            except Exception as e:
                print(f"commit file blame no ranges: {commit_file_blame}\n"
                      f"Exception: {e}")
                blame_ranges = None
                pass
            if blame_ranges:
                for range in blame_ranges:
                    try:
                        commit_sha = range['commit']['oid']
                    except Exception as e:
                        print(f"commit file blame range no commit oid: {commit_file_blame}\n"
                              f"Exception: {e}")
                        commit_sha = None
                        pass
                    if commit_sha:
                        commit_shas.add(commit_sha)
        return list(commit_shas)

    @staticmethod
    def get_hg_commit_shas_from_file_annotates(file_annotates):
        commit_shas = set()
        for file_annotate in tqdm(file_annotates, ascii=True):
            try:
                blame_ranges = file_annotate['annotate']
            except Exception as e:
                print(f"file_annotates no annotate: {file_annotate}\n"
                      f"Exception: {e}")
                blame_ranges = None
                pass
            if blame_ranges:
                for range in blame_ranges:
                    try:
                        commit_sha = range['node']
                    except Exception as e:
                        print(f"file_annotates annotate no node: {file_annotate}\n"
                              f"Exception: {e}")
                        commit_sha = None
                        pass
                    if commit_sha:
                        commit_shas.add(commit_sha)
        return list(commit_shas)

    @staticmethod
    def get_hg_commit_shas_from_file_annotates_with_test_commit(file_annotates, test_commit):
        commit_shas = set()
        for file_annotate in tqdm(file_annotates, ascii=True):
            if 'abspath' in file_annotate.keys():
                filepatch = test_commit.get_filepatch_by_filepath(file_annotate['abspath'])
            # print(filepatch)
                if filepatch:
                    modified_removed_lines = filepatch.get_modified_removed_lines()
                    if modified_removed_lines:
                        try:
                            blame_ranges = file_annotate['annotate']
                        except Exception as e:
                            print(f"file_annotates no annotate: {file_annotate}\n"
                                  f"Exception: {e}")
                            blame_ranges = None
                            pass
                        if blame_ranges:
                            for line in modified_removed_lines:
                                # print(line)

                                # print(range)
                            # for range in blame_ranges:
                            #     commit_sha = None
                                try:
                                    range = blame_ranges[line.no - 1]
                                    # if line.content == range['line'].strip and line.no == range['lineno']:
                                    commit_sha = range['node']
                                except Exception as e:
                                    print(f"file_annotates annotate no node: {file_annotate}\n"
                                          f"Exception: {e}")
                                    commit_sha = None
                                    pass
                                if commit_sha:
                                    # print(commit_sha)
                                    commit_shas.add(commit_sha)
        return list(commit_shas)

    @staticmethod
    def get_github_commit_shas_from_commits(commits):
        commit_shas = set()
        for commit in commits:
            try:
                commit_shas.add(commit['sha'])
            except Exception as e:
                print(f"commit no sha: {commit}\n"
                      f"Exception: {e}")
                pass
        return commit_shas

    # @staticmethod
    # def get_github_commit_sha_filenames_pairs_from_commit_dicts(commit_dicts):
    #     commit_sha_filename_dicts = []
    #     for commit_dict in tqdm(commit_dicts, ascii=True):
    #         commit_sha_filename_dict[commit_dict["sha"]] = commit_sha_filename_dict.get(commit_dict["sha"], )
    #         commit_shas.append(commit_dict["sha"])
    #     return commit_shas

    @staticmethod
    def get_github_commit_urls(owner_name, repo_name, commit_shas):
        commit_link = GITHUB_COMMIT_LINK.format(owner_name=owner_name, repo_name=repo_name)
        commit_urls = []
        # URL for the GitHub REST API to fetch the commit.
        for commit_sha in commit_shas:
            commit_url = commit_link + f'/{commit_sha}'
            commit_urls.append(commit_url)
        return commit_urls

    @staticmethod
    def get_hg_commit_urls(commit_shas):
        commit_urls = []
        # URL for the GitHub REST API to fetch the commit.
        for commit_sha in commit_shas:
            commit_url = COMMIT_MESSAGE_JSON_LINK + f'/{commit_sha}'
            commit_urls.append(commit_url)
        return commit_urls

    @staticmethod
    def get_github_commit_file_content_urls(owner_name, repo_name, commit_dicts):
        commit_file_content_urls = []
        # URL for the GitHub REST API to fetch the commit.
        for commit_dict in commit_dicts:
            for file in commit_dict['files']:
                commit_file_content_url = GITHUB_COMMIT_FILE_LINK.format(owner_name=owner_name, repo_name=repo_name,
                                                                         file_path=file['filename'],
                                                                         commit_oid=commit_dict['sha'])
                commit_file_content_urls.append(commit_file_content_url)
        return commit_file_content_urls

    @staticmethod
    def get_github_commits_diff_url_between_versions(ownername, reponame, from_version, to_version):
        # GitHub API endpoint for commits
        url = f"https://api.github.com/repos/{ownername}/{reponame}/compare/{from_version}...{to_version}"
        return url
        # # Sending GET request to GitHub API
        # response = requests.get(url)
        #
        # # Checking if request was successful
        # if response.status_code == 200:
        #     commits_data = response.json()
        #     return [commit['commit']['message'] for commit in commits_data['commits']]
        # else:
        #     print("Failed to fetch commits:", response.status_code)
        #     return []

    @staticmethod
    def get_github_commit_urls_from_commits_diff(commits_diff):
        commit_urls = []
        for commit in commits_diff['commits']:
            commit_urls.append(commit['url'])
        return commit_urls

    @staticmethod
    def get_github_issue_pull_close_relation_queries_for_graphql(ownername, reponame, issuenums):
        query = """
        {{
          repository(owner: "{username}", name: "{reponame}") {{
          issue(number: {issuenum}) {{
              timelineItems(first: 100) {{
                nodes {{
                  ... on ClosedEvent {{
                    closer {{
                      ... on PullRequest {{
                        number
                        title
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        queries = []
        for issuenum in tqdm(issuenums, ascii=True):
            one_query = query.format(username=ownername, reponame=reponame, issuenum=issuenum)
            queries.append(one_query)
        return queries

    @staticmethod
    def get_github_issue_pull_crossref_relation_queries_for_graphql(ownername, reponame, issuenums):
        # reference website: https://github.com/orgs/community/discussions/24367
        query = """
        {{
          repository(owner: "{username}", name: "{reponame}") {{
          issue(number: {issuenum}) {{
              timelineItems(first: 100) {{
                nodes {{
                  ... on CrossReferencedEvent {{
                    source {{
                      ... on PullRequest {{
                        number
                        title
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        queries = []
        for issuenum in tqdm(issuenums, ascii=True):
            one_query = query.format(username=ownername, reponame=reponame, issuenum=issuenum)
            queries.append(one_query)
        return queries

    @staticmethod
    def get_github_issue_pull_close_crossref_relation_queries_for_graphql(ownername, reponame, issuenums):
        # reference website: https://github.com/orgs/community/discussions/24367
        query = """
        {{
          repository(owner: "{username}", name: "{reponame}") {{
          issue(number: {issuenum}) {{
              timelineItems(first: 100) {{
                nodes {{
                  ... on ClosedEvent {{
                    closer {{
                      ... on PullRequest {{
                        number
                        title
                        url
                        repository {{
                            nameWithOwner
                        }}
                      }}
                    }}
                  }}
                  ... on CrossReferencedEvent {{
                    source {{
                      ... on PullRequest {{
                        number
                        title
                        url
                        repository {{
                            nameWithOwner
                        }}
                      }}
                      ... on Issue {{
                        number
                        title
                        url
                        repository {{
                            nameWithOwner
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        queries = []
        for issuenum in tqdm(issuenums, ascii=True):
            one_query = query.format(username=ownername, reponame=reponame, issuenum=issuenum)
            queries.append(one_query)
        return queries

    @staticmethod
    def get_github_pull_issue_close_crossref_relation_queries_for_graphql(ownername, reponame, pullnums):
        # reference website: https://github.com/orgs/community/discussions/24367
        query = """
        {{
          repository(owner: "{username}", name: "{reponame}") {{
          pullRequest(number: {pullnum}) {{
              timelineItems(first: 100) {{
                nodes {{
                  ... on ClosedEvent {{
                    closer {{
                      ... on PullRequest {{
                        number
                        title
                        url
                        repository {{
                            nameWithOwner
                        }}
                      }}
                    }}
                  }}
                  ... on CrossReferencedEvent {{
                    source {{
                      ... on PullRequest {{
                        number
                        title
                        url
                        repository {{
                            nameWithOwner
                        }}
                      }}
                      ... on Issue {{
                        number
                        title
                        url
                        repository {{
                            nameWithOwner
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        queries = []
        for pullnum in tqdm(pullnums, ascii=True):
            one_query = query.format(username=ownername, reponame=reponame, pullnum=pullnum)
            queries.append(one_query)
        return queries

    @staticmethod
    def get_github_commit_file_blame_queries_for_graphql(ownername, reponame, commit_dicts):
        query = """
        {{
          repository(owner: "{username}", name: "{reponame}") {{
                # branch name

              object(oid: "{commit_oid}") {{
                # cast Target to a Commit
                ... on Commit {{
                  # full repo-relative path to blame file
                         oid
                        blame(path:"{filepath}") {{
                            ranges {{
                              commit {{
                                oid
                              }}
                              startingLine
                              endingLine
                              age
                                }}
                            }}
                }}
              }}
            }}

        }}
        """
        files = []
        queries = []
        # commit_oid_filename_pairs = []
        for commit_dict in tqdm(commit_dicts, ascii=True):
            for file in commit_dict['files']:
                one_query = query.format(username=ownername, reponame=reponame,
                                         commit_oid=commit_dict['sha'], filepath=file['filename'])
                queries.append(one_query)
                files.append(file)
        return queries, files

