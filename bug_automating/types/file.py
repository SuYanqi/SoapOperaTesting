import base64
import os
from tqdm import tqdm

from bug_automating.types.bug import Bugs
from config import GITHUB_COMMIT_FILE_LINK, FILE_CONTENT_JSON_LINK, FILE_CONTENT_LINK


class Line:
    def __init__(self, file=None, line_no=None, line_content=None, last_commit=None):
        self.file = file  # object
        self.no = line_no  # start from 1
        self.content = line_content
        self.last_commit = last_commit  # object

    def __repr__(self):
        return f'{self.file.path} - {self.no} - {self.content} - {self.last_commit}'

    def __str__(self):
        return f'{self.file.path} - {self.no} - {self.content} - {self.last_commit}'

    def get_closed_issues(self):
        """
        get all directly linked issues for this line
        directly linked: link by last commit -> pulls -> issues
        return Bugs
        """
        pulls = Bugs(self.last_commit.bugs)
        issues = pulls.get_closed_issues()
        return issues


class Lines:
    def __init__(self, lines=None):
        if lines is None:
            lines = []
        self.lines = lines

    def __iter__(self):
        for line in self.lines:
            yield line

    def __getitem__(self, index):
        return self.lines[index]

    def __len__(self):
        return len(self.lines)

    def append(self, line):
        # Your custom append logic here
        self.lines.append(line)

    @classmethod
    def from_content(cls, file, content):
        lines = []
        if content:
            line_contents = content.splitlines()
            for index, line_content in enumerate(line_contents):
                line = Line(file, index + 1, line_content)
                lines.append(line)
        else:
            print(file.path)
        return cls(lines)

    def get_line_by_no(self, line_no):
        if line_no:
            for line in self.lines:
                if line.no == line_no:
                    return line
        # print(line_no)
        return None

    def get_line_last_commit_from_commit_file_blame(self, commit_file_blame, commits):
        try:
            blame_ranges = commit_file_blame['blame']['ranges']
        except Exception as e:
            # print(commit_file_content['html_url'])
            print(f"blame_ranges not existing: {commit_file_blame}\n"
                  f"Exception: {e}")
            blame_ranges = []
        for blame_range in blame_ranges:
            commit_id = None
            start_line = None
            end_line = None
            try:
                commit_id = blame_range["commit"]["oid"]
                start_line = blame_range["startingLine"]
                end_line = blame_range["endingLine"]
            except Exception as e:
                print(f"blame_range not right (commit id, startingLine, endingLine and age): {blame_range}\n"
                      f"Exception: {e}")
                pass
            commit = commits.get_commit_by_id(commit_id)
            if commit:
                for line_no in range(start_line, end_line + 1):
                    line = self.get_line_by_no(line_no)
                    if line:
                        line.last_commit = commit
                    # else:
                    #     print(line_no)
            else:
                print(f"commit object for Commit_id: {commit_id} not existing")

    def get_hg_line_last_commit_from_file_annotate(self, file_annotate, commits):
        try:
            blame_ranges = file_annotate['annotate']
        except Exception as e:
            # print(commit_file_content['html_url'])
            print(f"file_annotate annotate not existing: {file_annotate}\n"
                  f"Exception: {e}")
            blame_ranges = []
        for blame_range in blame_ranges:
            commit_id = None
            start_line = None
            end_line = None
            try:
                commit_id = blame_range["node"]
                start_line = blame_range["lineno"]
                end_line = blame_range["lineno"]
            except Exception as e:
                print(f"blame_range not right (commit id, startingLine, endingLine and age): {blame_range}\n"
                      f"Exception: {e}")
                pass
            commit = commits.get_commit_by_id(commit_id)
            if commit:
                for line_no in range(start_line, end_line + 1):
                    line = self.get_line_by_no(line_no)
                    if line:
                        line.last_commit = commit
                    # else:
                    #     print(line_no)
            else:
                print(f"commit object for Commit_id: {commit_id} not existing")

    def sort_lines_by_line_last_commit_date(self, reverse=True):
        self.lines.sort(key=lambda line: line.last_commit.date, reverse=reverse)


class Content:
    def __init__(self, file, raw_content=None, encoding=None, lines=None):
        self.file = file  # object
        self.raw_content = raw_content
        self.encoding = encoding
        self.lines = lines  # object

    def __repr__(self):
        return f'{self.file.path} - {self.file.type} - {self.file.html_url} - {self.encoding} - {len(self.lines)}'

    def __str__(self):
        return f'{self.file.path} - {self.file.type} - {self.file.html_url} - {self.encoding} - {len(self.lines)}'

    @classmethod
    def from_dict(cls, file, content, encoding):
        decoded_content = cls.decode_base64_encoded_content_by_utf8(content, encoding)
        lines = Lines.from_content(file, decoded_content)
        return cls(file, content, encoding, lines)

    @classmethod
    def from_hg_dict(cls, file_lines, file):
        content = ''
        for file_line in file_lines:
            content = content + file_line['line']
        lines = Lines.from_content(file, content)
        return cls(file, file_lines, None, lines)

    @staticmethod
    def decode_base64_encoded_content_by_utf8(content, encoding='base64'):
        if encoding == 'base64':
            # Decode the content using base64
            decoded_content = base64.b64decode(content)
            # print(decoded_content)
            # Return the decoded content
            try:
                # Only use UTF-8 for decoding 文本文件
                decoded_content = decoded_content.decode('utf-8')  # Adjust the encoding if needed
            except Exception as e:
                print(f"decoded_content.decode('utf-8'): {e}")
                return None
            return decoded_content
        else:
            if encoding is not None:
                print(f"Other encoding: {encoding}")
            return None


class File:
    def __init__(self, id=None, path=None, last_commit=None, content=None,
                 api_url=None, html_url=None, git_url=None, download_url=None,
                 certain_type=None, name=None, size=None, ):
        self.id = id  # file id: 10fed8d798d3f5a664f68b209dedfebd63ca6b5c
        self.path = path  # WordPress/src/main/java/org/wordpress/android/ui/mysite/SiteNavigationAction.kt
        self.last_commit = last_commit  # object : can use api url to get the commit sha first
        self.content = content  # object

        self.api_url = api_url  # contents_url in Commit: use last commit sha: https://api.github.com/repos/wordpress-mobile/WordPress-Android/contents/WordPress/src/main/java/org/wordpress/android/ui/mysite/SiteNavigationAction.kt?ref=f4703b8f17690f59700fea63f4480e6a4fe24479
        self.html_url = html_url  # blob_url in Commit: use last commit sha: https://github.com/wordpress-mobile/WordPress-Android/blob/f4703b8f17690f59700fea63f4480e6a4fe24479/WordPress/src/main/java/org/wordpress/android/ui/mysite/SiteNavigationAction.kt

        self.git_url = git_url  # use file sha: https://api.github.com/repos/wordpress-mobile/WordPress-Android/git/blobs/10fed8d798d3f5a664f68b209dedfebd63ca6b5c
        self.download_url = download_url  # use last commit sha: https://raw.githubusercontent.com/wordpress-mobile/WordPress-Android/f4703b8f17690f59700fea63f4480e6a4fe24479/WordPress/src/main/java/org/wordpress/android/ui/mysite/SiteNavigationAction.kt
        self.type = certain_type  # "file"
        self.name = name  # SiteNavigationAction.kt
        self.size = size  # 6548

    def __repr__(self):
        return f'{self.path} - {self.id} - {self.html_url}'

    def __str__(self):
        return f'{self.path} - {self.id} - {self.html_url}'

    @classmethod
    def from_commit_file_dict(cls, commit, file_dict):
        """
        commit is an object
        """
        file = cls(file_dict['sha'], file_dict['filename'], commit)
        file.api_url = file_dict['contents_url']
        file.html_url = file_dict['blob_url']
        return file

    @classmethod
    def from_path(cls, filepath):
        file = cls()
        file.path = filepath
        return file

    @classmethod
    def from_hg_file_content_dict(cls, file_content_dict):
        file = cls()
        try:
            file.path = file_content_dict['path']
            file.last_commit = file_content_dict['node']
            file.api_url = f"{FILE_CONTENT_JSON_LINK}{file_content_dict['node']}/{file_content_dict['path']}"
            file.html_url = f"{FILE_CONTENT_LINK}{file_content_dict['node']}/{file_content_dict['path']}"
            file.git_url = None
            file.download_url = None
            file.type = None
            file.name = None
            file.size = None
            # try:
            file.content = Content.from_hg_dict(file_content_dict['lines'], file)
            return file
        except Exception as e:
            # print(file_content_dict)
            print(f"from_hg_file_content_dict is wrong: {file_content_dict}\nException: {e}")
            return None

    def get_content_from_commit_file_content(self, commit_file_content):
        try:
            self.id = commit_file_content['sha']
            self.content = Content.from_dict(self, commit_file_content['content'], commit_file_content['encoding'])
            self.api_url = commit_file_content['url']
            self.html_url = commit_file_content['html_url']
            self.git_url = commit_file_content['git_url']
            self.download_url = commit_file_content['download_url']
            self.type = commit_file_content['type']
            self.name = commit_file_content['name']
            self.size = commit_file_content['size']
        except Exception as e:
            # print(commit_file_content['html_url'])
            print(f"get_content_from_commit_file_content is wrong: {commit_file_content['path']}\nException: {e}")

    @staticmethod
    def get_file_type_by_filepath(filepath):
        _, file_extension = os.path.splitext(filepath)
        return file_extension.lower()  # Convert to lowercase for consistency

    def get_file_type(self):
        return self.get_file_type_by_filepath(self.path)  # Convert to lowercase for consistency

    def get_directly_linked_pulls(self):
        """
        get all directly linked pulls for this file
        directly linked: link by last commit
        return Bugs
        """
        pulls = set()
        for line in self.content.lines:
            pulls = pulls.union(set(line.last_commit.bugs))
            # print(line)
            # for bug in line.last_commit.bugs:
            #     print(bug)
            # print('******************************************')
        return Bugs(list(pulls))

    def get_closed_issues(self):
        """
        get all directly linked issues for this file
        directly linked: link by last commit -> pull -> issue
        return Bugs
        """
        pulls = self.get_directly_linked_pulls()
        issues = pulls.get_closed_issues()
        return issues

    def get_last_commit(self):
        """
        get the last commit, modifying this file
        """
        all_commits = []
        for line in self.content.lines:
            all_commits.append(line.last_commit)
        all_commits = sorted(all_commits, key=lambda x: x.date, reverse=True)
        return all_commits[0]

    # @classmethod
    # def from_github_dict(cls, file_dict):
    #     '''
    #     @todo commit?
    #     '''
    #     file = cls(file_dict['name'], file_dict['path'], file_dict["sha"], file_dict["size"],
    #                file_dict['url'], file_dict['html_url'], file_dict['git_url'], file_dict['download_url'],
    #                file_dict['type'])
    #     content = Content(file, file_dict['content'], file_dict['encoding'])
    #     file.content = content
    #     return file


class Files:
    def __init__(self, files=[], last_commit=None):
        self.files = files
        self.last_commit = last_commit

    def __iter__(self):
        for file in self.files:
            yield file

    def __getitem__(self, index):
        return self.files[index]

    def __len__(self):
        return len(self.files)

    def append(self, file):
        # Your custom append logic here
        self.files.append(file)

    @classmethod
    def from_paths(cls, filepaths, last_commit=None):
        files = []
        for filepath in filepaths:
            file = File.from_path(filepath)
            files.append(file)
        return cls(files, last_commit)

    @classmethod
    def from_hg_file_content_dicts(cls, file_content_dicts):
        files = []
        try:
            last_commit = file_content_dicts[0]['node']
        except:
            last_commit = None
            pass
        for file_content_dict in file_content_dicts:
            file = File.from_hg_file_content_dict(file_content_dict)
            if file:
                files.append(file)
        return cls(files, last_commit)

    @staticmethod
    def get_all_filepaths_under_directory(directory):
        """
        return filepaths: string list
        """
        filepath_list = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_path = file_path.replace(f"{directory}/", "")
                filepath_list.append(file_path)
        return filepath_list

    def from_commit_file_dicts(self, commit, file_dicts=None):
        """
        commit is an object
        file_dicts:
        """
        if file_dicts is None:
            file_dicts = commit.files
        for file_dict in file_dicts:
            if self.get_file_by_filepath(file_dict['filename']) is None:
                file = File.from_commit_file_dict(commit, file_dict)
                self.append(file)

    def get_file_by_filepath(self, filepath):
        for file in self.files:
            if file.path == filepath:
                return file
        return None

    def get_filetype_files_dict(self):
        filetype_files_dict = dict()
        for file in self.files:
            filetype = file.get_file_type()
            filetype_files_dict[filetype] = filetype_files_dict.get(filetype, [])
            filetype_files_dict[filetype].append(file)
        filetype_files_dict = dict(sorted(filetype_files_dict.items(), key=lambda item: len(item[1]), reverse=True))
        return filetype_files_dict

    def get_github_commit_file_blame_queries_for_graphql(self, ownername, reponame):
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
        if type(self.last_commit) is str:
            commit_id = self.last_commit
        else:
            commit_id = self.last_commit.id
        for file in tqdm(self.files, ascii=True):
            # one_query = query.format(username=ownername, reponame=reponame,
            #                          commit_oid=file.last_commit.id, filepath=file.path)
            one_query = query.format(username=ownername, reponame=reponame,
                                     commit_oid=commit_id, filepath=file.path)
            queries.append(one_query)
            files.append(file.path)
        return queries, files

    def get_github_commit_file_content_urls(self, ownername, reponame):
        commit_file_content_urls = []
        if type(self.last_commit) is str:
            commit_id = self.last_commit
        else:
            commit_id = self.last_commit.id
        for file in tqdm(self.files, ascii=True):
            # commit_file_content_url = GITHUB_COMMIT_FILE_LINK.format(owner_name=ownername, repo_name=reponame,
            #                                                          file_path=file.path,
            #                                                          commit_oid=file.last_commit.id)
            commit_file_content_url = GITHUB_COMMIT_FILE_LINK.format(owner_name=ownername, repo_name=reponame,
                                                                     file_path=file.path,
                                                                     commit_oid=commit_id)
            commit_file_content_urls.append(commit_file_content_url)
        return commit_file_content_urls

    def filter_by_existing_filepaths(self, existing_filepaths):
        # @todo existing filepaths - filtered filepaths > 0
        file_list = []
        for file in self.files:
            # print(file.path)
            # print(type(file.path))
            if file.path in existing_filepaths:
                file_list.append(file)
        return Files(file_list)

    def get_file_content_from_commit_file_contents(self, commit_file_contents):
        for commit_file_content in tqdm(commit_file_contents, ascii=True):
            try:
                filepath = commit_file_content['path']
            except Exception as e:
                print(f"commit_file_content is invalid: {commit_file_content}\nException: {e}")
                filepath = None
            if filepath:
                # print(filepath)
                # print(commit_file_content)
                file = self.get_file_by_filepath(filepath)
                # print(file)
                if file:
                    file.get_content_from_commit_file_content(commit_file_content)
                else:
                    print(f"file object is None: {filepath}")

    def get_line_last_commit_by_commit_file_blames(self, commit_file_blames, commits):
        for commit_file_blame in tqdm(commit_file_blames, ascii=True):
            try:
                filepath = commit_file_blame['filename']
            except Exception as e:
                print(f"commit_file_blame is invalid: {commit_file_blame}\n"
                      f"Exception: {e}")
                filepath = None
            if filepath:
                # print(filepath)
                # print(commit_file_content)
                file = self.get_file_by_filepath(filepath)
                print(file)
                if file:
                    if file.content:
                        if file.content.lines:
                            file.content.lines.get_line_last_commit_from_commit_file_blame(commit_file_blame, commits)
                else:
                    print(f"file object is None: {filepath}")

    def get_hg_line_last_commit_by_file_annotates(self, file_annotates, commits):
        for file_annotate in tqdm(file_annotates, ascii=True):
            try:
                filepath = file_annotate['abspath']
            except Exception as e:
                print(f"file_annotate is invalid: {file_annotate}\n"
                      f"Exception: {e}")
                filepath = None
            if filepath:
                # print(filepath)
                # print(commit_file_content)
                file = self.get_file_by_filepath(filepath)
                print(file)
                if file:
                    if file.content:
                        if file.content.lines:
                            file.content.lines.get_hg_line_last_commit_from_file_annotate(file_annotate, commits)
                else:
                    print(f"file object is None: {filepath}")

    def get_directly_linked_pulls(self):
        pulls = set()
        for file in self.files:
            file_pulls = file.get_directly_linked_pulls()
            pulls = pulls.union(set(file_pulls))
        return Bugs(list(pulls))

    def get_modified_deleted_lines_by_test_commit(self, test_commit):
        # todo filter lines by line content with useless content, e.g., space, {, }
        lines = []
        for file_patch in test_commit.file_patches:
            # print(f"file_patch: {file_patch}")
            file = self.get_file_by_filepath(file_patch.filepath)
            # print(file)
            if file:
                for patch_content in file_patch.patch_contents:
                    for before_patch_line in patch_content.before_patch_lines:
                        # only focus on delete and modify, cannot handle add now
                        if before_patch_line.status == '-':
                            # print(before_patch_line)
                            line = file.content.lines.get_line_by_no(before_patch_line.no)
                            if line:
                                # need to filter lines with useless content, e.g., space, {, }
                                if line.content == before_patch_line.content:
                                    lines.append(line)
                                    # print(line)
        return lines
