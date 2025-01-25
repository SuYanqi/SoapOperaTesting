import re
from datetime import datetime

from tqdm import tqdm

from bug_automating.types.file import File
from bug_automating.utils.datetime_util import DatetimeUtil
from bug_automating.utils.dict_util import DictUtil
from config import COMMIT_MESSAGE_LINK, COMMIT_MESSAGE_JSON_LINK, FILE_CONTENT_LINK, FILE_CONTENT_JSON_LINK, \
    FILE_ANNOTATES_JSON_LINK, COMMIT_DATETIME_FORMAT


class PatchLine:
    def __init__(self, line_no=None, line_content=None, status=None):
        self.no = line_no
        self.content = line_content
        self.status = status  # -: delete, +: add, space: no change

    def __repr__(self):
        return f'{self.no} * {self.status} * {self.content}'

    def __str__(self):
        return f'{self.no} * {self.status} * {self.content}'


# class PatchLines:
#     def __init__(self, patch_lines=[]):
#         self.patch_lines = patch_lines
#
#     def __iter__(self):
#         for patch_line in self.patch_lines:
#             yield patch_line
#
#     def __getitem__(self, index):
#         return self.patch_lines[index]
#
#     def __len__(self):
#         return len(self.patch_lines)


class PatchContent:
    def __init__(self, text, prev_start_line_no=None, prev_end_line_no=None, start_line_no=None, end_line_no=None,
                 before_patch_lines=None, after_patch_lines=None):
        self.text = text
        self.prev_start_line_no = prev_start_line_no
        self.prev_end_line_no = prev_end_line_no
        self.start_line_no = start_line_no
        self.end_line_no = end_line_no
        self.before_patch_lines = before_patch_lines
        self.after_patch_lines = after_patch_lines

    def __repr__(self):
        return f'@@ {self.prev_start_line_no}, {self.prev_end_line_no} {self.start_line_no}, {self.end_line_no} @@'

    def __str__(self):
        return f'@@ {self.prev_start_line_no}, {self.prev_end_line_no} {self.start_line_no}, {self.end_line_no} @@'

    @classmethod
    def from_dict(cls, patch_str):
        patch_content = cls(patch_str)
        patch_content.get_line_nos()
        patch_content.get_lines()
        return patch_content

    def get_line_nos(self):
        pattern = r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@'
        matches = re.findall(pattern, self.text)
        self.prev_start_line_no = int(matches[0][0])
        self.prev_end_line_no = int(matches[0][0]) + int(matches[0][1])
        if self.prev_end_line_no > 0:
            self.prev_end_line_no = self.prev_end_line_no - 1
        self.start_line_no = int(matches[0][2])
        self.end_line_no = int(matches[0][2]) + int(matches[0][3])
        if self.end_line_no > 0:
            self.end_line_no = self.end_line_no - 1
        # for match in matches:
        #     print("From:", match[0], "To:", match[1], "and From:", match[2], "To:", match[3])

    def get_lines(self):
        lines = self.text.splitlines()[1:]
        pattern = r'^(\+|-| )(.*)$'
        self.before_patch_lines = []
        self.after_patch_lines = []
        prev_line_no = self.prev_start_line_no
        after_line_no = self.start_line_no
        # Iterate over each line and extract '+/-/None' from the start of each line
        for line in lines:
            match = re.match(pattern, line)
            if match:
                status = match.group(1)
                line_content = match.group(2)
                if status in ('-', ' '):
                    self.before_patch_lines.append(PatchLine(prev_line_no, line_content, status))
                    prev_line_no = prev_line_no + 1
                if status in ('+', ' '):
                    self.after_patch_lines.append(PatchLine(after_line_no, line_content, status))
                    after_line_no = after_line_no + 1

                # print(match.group(1))
                # print(match.group(2))


# class PatchContents:
#     def __init__(self, patch_contents=[]):
#         self.patch_contents = patch_contents
#
#     def __iter__(self):
#         for patch_content in self.patch_contents:
#             yield patch_content
#
#     def __getitem__(self, index):
#         return self.patch_contents[index]
#
#     def __len__(self):
#         return len(self.patch_contents)
#
#     def append(self, patch_content):
#         # Your custom append logic here
#         self.patch_contents.append(patch_content)
#
#     @classmethod
#     def from_dicts(cls, patch_blocks):
#         patch_contents = PatchContents()
#         for patch_block in patch_blocks:
#             patch_content = PatchContent.from_dict(patch_block)
#             # for line in patch_content.before_patch_lines:
#             #     print(line)
#             # print("***")
#             patch_contents.append(patch_content)
#         return patch_contents


class FilePatch:
    def __init__(self, file_id=None, filepath=None,
                 status=None, additions=None, deletions=None, changes=None,
                 html_url=None, api_url=None,
                 patch_contents=None):
        # self.commit = commit  # object
        self.file_id = file_id
        self.filepath = filepath
        self.status = status
        self.additions = additions
        self.deletions = deletions
        self.changes = changes
        self.html_url = html_url  # blob_url
        self.api_url = api_url  # contents_url
        self.patch_contents = patch_contents

    def __repr__(self):
        return f'{self.filepath} * {self.html_url} * {self.status} * {len(self.patch_contents)}'

    def __str__(self):
        return f'{self.filepath} * {self.html_url} * {self.status} * {len(self.patch_contents)}'

    @classmethod
    def from_dict(cls, file_patch_dict):
        patch_blocks = FilePatch.split_patch_blocks(file_patch_dict['patch'])
        patch_contents = []
        for patch_block in patch_blocks:
            patch_content = PatchContent.from_dict(patch_block)
            # for line in patch_content.before_patch_lines:
            #     print(line)
            # print("***")
            patch_contents.append(patch_content)
        # patch_contents = PatchContents.from_dicts(patch_blocks)
        # print("ok")
        return cls(file_patch_dict['sha'], file_patch_dict['filename'], file_patch_dict['status'],
                   file_patch_dict['additions'], file_patch_dict['deletions'], file_patch_dict['changes'],
                   file_patch_dict['blob_url'], file_patch_dict['contents_url'], patch_contents)

    @classmethod
    def from_hg_dict(cls, file_patch_dict):
        # filepath = cls.get_hg_filename(file_patch_dict)
        # print(filepath)
        patch_blocks = FilePatch.split_hg_patch_blocks(file_patch_dict['lines'])
        patch_contents = []
        for patch_block in patch_blocks:
            # print(patch_block)
            patch_content = PatchContent.from_dict(patch_block)
            # for line in patch_content.before_patch_lines:
            #     print(line)
            # print("***")
            patch_contents.append(patch_content)
        # patch_contents = PatchContents.from_dicts(patch_blocks)
        # print("ok")
        return cls(None, None, None,
                   None, None, None,
                   None, None, patch_contents)

    @staticmethod
    def split_patch_blocks(patch_str):
        # Splitting the patch string by the desired pattern
        patch_blocks = re.split(r'(?=@@ -\d+,\d+ \+\d+,\d+ @@)', patch_str)[1:]
        return patch_blocks

    @staticmethod
    def split_hg_patch_blocks(patch_lines):
        patch_str = ''
        for patch_line in patch_lines:
            if (not patch_line['l'].startswith("---")) and (not patch_line['l'].startswith("+++")):
                patch_str = patch_str + patch_line['l']
        # Splitting the patch string by the desired pattern
        patch_blocks = re.split(r'(?=@@ -\d+,\d+ \+\d+,\d+ @@)', patch_str)[1:]
        return patch_blocks

    @staticmethod
    def get_hg_filename(file_patch_dict):
        file_path = file_patch_dict["lines"][0]['l']
        # Remove leading "--- a/" and trailing newline character
        file_path = file_path[6:].rstrip('\n')
        return file_path

    @staticmethod
    def get_filepatch_list(file_patch_dict_list):
        file_patches = list()
        for file_patch_dict in file_patch_dict_list:
            # print(file_patch_dict)
            file_patch = FilePatch.from_dict(file_patch_dict)
            # print(file_patch)
            file_patches.append(file_patch)
            # print("#########################")
        return file_patches

    @staticmethod
    def get_hg_filepatch_list(commit_dict):
        file_patch_dict_list = commit_dict['diff']
        file_patches = list()
        for index, file_patch_dict in enumerate(file_patch_dict_list):
            # print(file_patch_dict)
            file_patch = FilePatch.from_hg_dict(file_patch_dict)
            file_patch.filepath = commit_dict['files'][index]['file']
            file_patch.status = commit_dict['files'][index]['status']
            file_patch.html_url = f"{FILE_CONTENT_LINK}{commit_dict['node']}/{file_patch.filepath}"
            file_patch.api_url = f"{FILE_CONTENT_JSON_LINK}{commit_dict['node']}/{file_patch.filepath}"
            # print(file_patch)
            file_patches.append(file_patch)
            # print("#########################")
        return file_patches

    def get_modified_removed_lines(self):
        lines = []
        for patch_content in self.patch_contents:
            for before_patch_line in patch_content.before_patch_lines:
                # only focus on delete and modify, cannot handle add now
                if before_patch_line.status == '-':
                    # print(f"before_patch_line: {before_patch_line}")
                    lines.append(before_patch_line)
        return lines

    def get_impacted_lines(self, file):
        lines = []
        for patch_content in self.patch_contents:
            for before_patch_line in patch_content.before_patch_lines:
                # only focus on delete and modify, cannot handle add now
                if before_patch_line.status == '-':
                    # print(f"before_patch_line: {before_patch_line}")
                    line = file.content.lines.get_line_by_no(before_patch_line.no)
                    if line:
                        # print(f"line: {line}")
                        # need to filter lines with useless content, e.g., space, {, }
                        if line.content == before_patch_line.content:
                            lines.append(line)
        return lines


# class FilePatches:
#     """
#     @todo remove?
#     """
#     def __init__(self, file_patches=[]):
#         self.file_patches = file_patches
#
#     def __iter__(self):
#         for patch_patch in self.file_patches:
#             yield patch_patch
#
#     def __getitem__(self, index):
#         return self.file_patches[index]
#
#     def __len__(self):
#         return len(self.file_patches)
#
#     def append(self, file_patch):
#         # Your custom append logic here
#         self.file_patches.append(file_patch)
#
#     @classmethod
#     def from_dicts(cls, file_patch_dict_list):
#         file_patches = cls()
#         for file_patch_dict in file_patch_dict_list:
#             # print(file_patch_dict)
#             file_patch = FilePatch.from_dict(file_patch_dict)
#             # print(file_patch)
#             file_patches.append(file_patch)
#             # print("#########################")
#         return file_patches


class Commit:

    def __init__(self, id=None, message=None, comment_count=None, date=None,
                 api_url=None, html_url=None, comments_url=None, commit_parents=None, files=None, file_patches=None, push_date=None):
        self.id = id
        self.message = message
        self.comment_count = comment_count
        self.date = date  # for hg is the creation time
        self.api_url = api_url
        self.html_url = html_url
        self.comments_url = comments_url

        # 1. use dict 2. need to covert into objects
        self.commit_parents = commit_parents  # object: use sha to find parent commits to replace
        self.files = files  # object: use file_dicts and then convert into objects
        self.file_patches = file_patches
        self.push_date = push_date  # for hg is the push time

        self.bugs = []  # issue, pull objects

        # self.diffs = diffs
        # self.date = date
        # self.backed_out_by = backed_out_by
        # self.branch = branch
        # self.bookmarks = bookmarks
        # self.tags = tags
        # self.user = user
        # self.parents = parents
        # self.phase = phase
        # self.pushid = pushid
        # self.pushdate = pushdate
        # self.pushuser = pushuser
        # self.landing_system = landing_system

    def __repr__(self):
        return f'{self.html_url}:\n\tDate: {self.date}\n\tMessage: {self.message}'

    def __str__(self):
        return f'{self.html_url}:\n\tDate: {self.date}\n\tMessage: {self.message}'

    @classmethod
    def from_dict(cls, commit_dict, with_file_patch=False):
        try:
            commit_date = datetime.strptime(commit_dict['commit']['author']['date'], COMMIT_DATETIME_FORMAT)
            if with_file_patch:
                file_patches = FilePatch.get_filepatch_list(commit_dict['files'])
                return cls(commit_dict['sha'], commit_dict['commit']['message'], commit_dict['commit']['comment_count'],
                           commit_date,
                           commit_dict['url'], commit_dict['html_url'], commit_dict['comments_url'],
                           commit_dict['parents'], commit_dict['files'], file_patches)
            return cls(commit_dict['sha'], commit_dict['commit']['message'], commit_dict['commit']['comment_count'],
                       commit_date,
                       commit_dict['url'], commit_dict['html_url'], commit_dict['comments_url'],
                       commit_dict['parents'], commit_dict['files'])
        except Exception as e:
            print(f"{e}: {commit_dict}")
            # print(f"{e}")
            return None

    @classmethod
    def from_hg_dict(cls, commit_dict, with_file_patch=False):
        # @todo crawel milestone for version and treeherder for repo
        try:
            # print(commit_dict['date'])
            commit_date = DatetimeUtil.comvert_timestamp_into_readable_format(commit_dict['date'][0])
            # print(commit_date)
            push_date = DatetimeUtil.comvert_timestamp_into_readable_format(commit_dict['pushdate'][0])
            # print(push_date)
            file_patches = None
            if with_file_patch:
                file_patches = FilePatch.get_hg_filepatch_list(commit_dict)
                # print("OK")
            return cls(commit_dict['node'], commit_dict['desc'], None,
                       commit_date,
                       f'{COMMIT_MESSAGE_JSON_LINK}{commit_dict["node"]}',
                       f'{COMMIT_MESSAGE_LINK}{commit_dict["node"]}', None,
                       commit_dict['parents'], commit_dict['files'], file_patches, push_date)
        except Exception as e:
            # print(f"{e}: {commit_dict}")
            print(f"{e}")
            return None

    def get_bug_id_from_message(self):
        pattern = r"Bug (\d+)"
        # Search for the bug ID in the string
        match = re.search(pattern, self.message)
        # Check if a match is found
        if match:
            bug_id = match.group(1)
            return bug_id
        return None

    def link_hg_bug_with_commit(self, bugs):
        bug_id = self.get_bug_id_from_message()
        if bug_id:
            bug = bugs.get_bug_by_id(bug_id)
            if bug:
                self.bugs.append(bug)
                bug.commits.append(self)

    def filter_file_dicts_by_existing_filepaths(self, existing_filepaths):
        file_dict_list = []
        for file_dict in self.files:
            if file_dict['filename'] in existing_filepaths:
                file_dict_list.append(file_dict)
        return file_dict_list

    def get_changed_filepatchs(self):
        """
        get all changed (status: added, modified, removed) filepaths from file_patches
        """
        # print(self)
        changed_filepaths = []
        for file_patch in self.file_patches:
            # changed_filepaths.append(file_patch.filepath)
            changed_filepaths.append(file_patch)
            # print(file_patch.filepath)
        # print("************************************")
        return changed_filepaths

    def get_filepatch_by_filepath(self, filepath):
        for filepatch in self.file_patches:
            if filepatch.filepath == filepath:
                return filepatch
        return None

    def get_modified_removed_filepatchs(self):
        """
        get changed (status: added, modified) filepaths from file_patches
        """
        # print(self)
        changed_filepaths = []
        for file_patch in self.file_patches:
            # changed_filepaths.append(file_patch.filepath)
            if file_patch.status in ['modified', 'removed']:
                changed_filepaths.append(file_patch)
                # changed_filepaths.append(file_patch.filepath)
            # print(file_patch.filepath)
        # print("************************************")
        return changed_filepaths

    def get_modified_removed_lines_from_file_patches(self):
        """
        get all changed lines (modified, removes) from file_patches
        """
        changed_lines = []
        for file_patch in self.file_patches:
            lines = file_patch.get_modified_removed_lines()
            changed_lines.extend(lines)
        return changed_lines

    def get_impacted_files_in_files_by_file_patches(self, files):
        """
        get impacted files (deleted, modified) (in repo) by file patches
        """
        impacted_files = []
        for file_patch in self.file_patches:
            file = files.get_file_by_filepath(file_patch.filepath)
            if file:
                impacted_files.append(file)
        return impacted_files

    def get_impacted_lines_in_files_by_file_patches(self, files):
        """
        get impacted lines (deleted, modified) (in repo) by file patches
        """
        impacted_lines = []
        if self.file_patches:
            for file_patch in self.file_patches:
                file = files.get_file_by_filepath(file_patch.filepath)
                if file:
                    # print(file)
                    # file_last_commit = file.get_last_commit()
                    # print(f"file_last_commit: {file_last_commit}")
                    lines = file_patch.get_impacted_lines(file)
                    impacted_lines.extend(lines)
        return impacted_lines

    def get_impacted_pulls_issues_by_file_patches(self, files):
        pull_count_dict = {}
        issue_count_dict = {}
        lines = self.get_impacted_lines_in_files_by_file_patches(files)
        for line in lines:
            for pull in line.last_commit.bugs:
                # print(pull)
                pull_count_dict[pull] = pull_count_dict.get(pull, 0) + 1
            issues = line.get_closed_issues()
            for issue in issues:
                # print(issue)
                issue_count_dict[issue] = issue_count_dict.get(issue, 0) + 1
            # print('##################')
        pull_count_dict = DictUtil.sort_bug_count_dict_by_count_creation_time(pull_count_dict)
        issue_count_dict = DictUtil.sort_bug_count_dict_by_count_creation_time(issue_count_dict)
        # pull_count_dict = dict(sorted(pull_count_dict.items(), key=lambda item: item[1], reverse=True))
        # issue_count_dict = dict(sorted(issue_count_dict.items(), key=lambda item: item[1], reverse=True))
        return pull_count_dict, issue_count_dict

    def get_hg_commit_parent_file_content_urls(self):
        # print(f"commit parents: {self.commit_parents}")
        file_content_urls = []
        for commit_parent_id in self.commit_parents:
            for file_patch in self.file_patches:
                file_content_url = f"{FILE_CONTENT_JSON_LINK}{commit_parent_id}/{file_patch.filepath}"
                file_content_urls.append(file_content_url)
        return file_content_urls

    def get_hg_commit_parent_file_annotate_urls(self):
        file_content_urls = []
        for commit_parent_id in self.commit_parents:
            for file_patch in self.file_patches:
                file_content_url = f"{FILE_ANNOTATES_JSON_LINK}{commit_parent_id}/{file_patch.filepath}"
                file_content_urls.append(file_content_url)
        return file_content_urls


class Commits:
    def __init__(self, commits=[]):
        self.commits = commits

    def __iter__(self):
        for commit in self.commits:
            yield commit

    def __getitem__(self, index):
        return self.commits[index]

    def __len__(self):
        return len(self.commits)

    @classmethod
    def from_dicts(cls, commit_dicts, with_file_patch=False):
        commits = []
        for commit_dict in tqdm(commit_dicts, ascii=True):
            commit = Commit.from_dict(commit_dict, with_file_patch)
            if commit:
                commits.append(commit)
        return cls(commits)
        # return commits

    @classmethod
    def from_hg_dicts(cls, commit_dicts, with_file_patch=False):
        commits = []
        for commit_dict in tqdm(commit_dicts, ascii=True):
            # print("OK")
            commit = Commit.from_hg_dict(commit_dict, with_file_patch)
            # print("OK")
            if commit:
                commits.append(commit)
                # print(commit)
        return cls(commits)

    def append(self, commit):
        # Your custom append logic here
        self.commits.append(commit)
        # print(f"Appended: {item}")

    def get_bug_ids_from_message(self):
        bug_ids = set()
        for commit in self.commits:
            bug_id = commit.get_bug_id_from_message()
            if bug_id:
                bug_ids.add(bug_id)
        # remove space
        bug_ids = [int(x.strip()) for x in list(bug_ids)]
        bug_ids.sort(reverse=True)
        return bug_ids

    def link_hg_bugs_with_commits(self, bugs):
        for index, commit in tqdm(enumerate(self.commits), ascii=True):
            commit.link_hg_bug_with_commit(bugs)

    def get_commit_by_id(self, id):
        if id:
            for commit in self.commits:
                if commit.id == id:
                    # print(commit)
                    return commit
        # print(id)
        return None

    def get_commits_by_id(self, id):
        commits = []
        if id:
            for commit in self.commits:
                if commit.id == id:
                    # print(commit)
                    # return commit
                    commits.append(commit)
        # print(id)
        return commits

    def sort_commits_by_date(self, reverse=True):
        self.commits = sorted(self.commits, key=lambda x: x.date, reverse=reverse)

    def split_commits_by_percentage(self, percentage=0.8):
        """
        1. sort by date in reverse order
        2. split by percentage
        3. return train_commits and test_commits
        """
        self.sort_commits_by_date()
        split_index = round(len(self) * (1 - percentage))  # 四舍五入
        return Commits(self[split_index:]), Commits(self[0: split_index])
        # for index, commit in enumerate(self.commits):
        #     if commit.id == commit_id:
        #         return self[0: index], self[index:]

    def split_commits_into_complete_added_and_incomplete(self, files):
        """
        split commits into complete: all changed lines are found and can get all their impacted pulls and issues
                           all added: all changed lines are added lines
                           incomplete: not all changed lines are found
        """
        complete_commits = []
        all_added_commits = []
        incomplete_commits = []
        for commit in self.commits:
            # changed_files = commit.get_changed_filepaths()
            # changed_files = commit.get_modified_removed_filepatchs()
            # impacted_files = commit.get_impacted_files_in_files_by_file_patches(files)
            # impacted_filepaths = []
            # for impacted_file in impacted_files:
            #     impacted_filepaths.append(impacted_file.path)
            # # file level indentification
            # if len(changed_files) != len(impacted_files):
            #     incomplete_commits.append(commit)
            #     continue
            modified_deleted_lines = commit.get_modified_removed_lines_from_file_patches()
            impacted_lines = commit.get_impacted_lines_in_files_by_file_patches(files)
            if len(modified_deleted_lines) != len(impacted_lines):
                incomplete_commits.append(commit)
                # print(commit)
                # print(len(modified_deleted_lines))
                # print(len(impacted_lines))
                # # for changed_file in changed_files:
                # #     if changed_file.filepath not in impacted_filepaths:
                # #         print(changed_file.filepath)
                # #         print(changed_file.status)
                # print("#################")
                # print(len(changed_files))
                # print(len(impacted_files))
                # for changed_file in changed_files:
                #     if changed_file.filepath not in impacted_filepaths:
                #         print(changed_file.filepath)
                #         print(changed_file.status)
                # print("#################")
            elif len(impacted_lines) == 0:
                all_added_commits.append(commit)
            else:
                complete_commits.append(commit)
        return complete_commits, all_added_commits, incomplete_commits

    def split_commits_into_unmerge_and_merge(self):
        unmerge_commits = []
        merge_commits = []
        for commit in self.commits:
            if "Merge" in commit.message:
                merge_commits.append(commit)
            else:
                unmerge_commits.append(commit)
        return unmerge_commits, merge_commits

    def get_filetype_count_dict(self):
        filetype_count_dict = dict()
        for commit in self.commits:
            for filepath in commit.files:
                if type(filepath) is str:
                    filetype = File.get_file_type_by_filepath(filepath)
                elif type(filepath) is dict:
                    filetype = File.get_file_type_by_filepath(filepath['filename'])
                else:
                    filetype = filepath.get_file_type()
                filetype_count_dict[filetype] = filetype_count_dict.get(filetype, 0) + 1
        return filetype_count_dict

    def get_missing_commit_ids(self, commit_shas):
        # missing_commit_ids = []
        all_commit_ids = self.get_commit_ids()
        missing_commit_ids = list(set(commit_shas) - set(all_commit_ids))
        return missing_commit_ids
        # for commit_sha in commit_shas:
        #     commit = self.get_commit_by_id(commit_sha)
        #     if commit is None:
        #         missing_commit_ids.append(commit_sha)
        # return missing_commit_ids

    def get_commit_ids(self):
        commit_ids = []
        for commit in self.commits:
            commit_ids.append(commit.id)
        return commit_ids

    def get_changed_filepaths(self):
        changed_filepaths = []
        for commit in self.commits:
            changed_filepaths.extend(commit.get_changed_filepatchs())
        return list(set(changed_filepaths))

    def get_merge_commits(self):
        # @todo
        merge_commits = []
        for commit in self.commits:
            if "Merge" in commit.message:
                merge_commits.append(commit)
        return merge_commits

# class Annotate:
#     def __init__(self, commit=None, file=None, target_line=None, line=None, lineno=None, revdate=None):
#         self.commit = commit  # object
#         self.file = file  # object
#         self.target_line = target_line
#         self.line = line
#         self.lineno = lineno
#         self.revdate = revdate
#
#     def __repr__(self):
#         if type(self.commit) is Commit:
#             return f'{self.commit.id} - {self.target_line} - {self.line}'
#         else:
#             return f'{self.commit} - {self.target_line} - {self.line}'
#
#     def __str__(self):
#         if type(self.commit) is Commit:
#             return f'{self.commit.id} - {self.target_line} - {self.line}'
#         else:
#             return f'{self.commit} - {self.target_line} - {self.line}'
#
#     @classmethod
#     def from_dict(cls, annotate_dict, commits):
#         try:
#             commit = commits.get_commit_by_node(annotate_dict['node'])
#         except Exception as e:
#             logging.warning(e)
#             logging.warning(annotate_dict)
#             commit = None
#
#         if commit:
#             file = commit.files.get_file_by_filepath(annotate_dict['abspath'])
#             annotate = cls(commit, file, annotate_dict['targetline'], annotate_dict['line'],
#                            annotate_dict['lineno'], annotate_dict['revdate'])
#         else:
#             # get commit id and filepath
#             annotate = cls(annotate_dict['node'], annotate_dict['abspath'], annotate_dict['targetline'],
#                            annotate_dict['line'],
#                            annotate_dict['lineno'], annotate_dict['revdate'])
#         return annotate
#
#         # return None
#
#
# class FileAnnotate:
#     def __init__(self, commit=None, file=None, annotates=None):
#         self.commit = commit  # object
#         self.file = file  # object
#         self.annotates = annotates
#
#     def __iter__(self):
#         for annotate in self.annotates:
#             yield annotate
#
#     def __getitem__(self, index):
#         return self.annotates[index]
#
#     def __len__(self):
#         return len(self.annotates)
#
#     @classmethod
#     def from_dict(cls, annotate_dict, commits):
#         try:
#             commit = commits.get_commit_by_node(annotate_dict['node'])
#         except Exception as e:
#             logging.warning(e)
#             logging.warning(annotate_dict)
#             commit = None
#
#         if commit:
#             annotates = []
#             file = commit.files.get_file_by_filepath(annotate_dict['abspath'])
#             for one_annotate_dict in annotate_dict['annotate']:
#                 annotate = Annotate.from_dict(one_annotate_dict, commits)
#                 if annotate:
#                     annotates.append(annotate)
#             file_annotate = cls(commit, file, annotates)
#             file.file_annotate = file_annotate
#             return file_annotate
#             # print(annotate_dict)
#         return None
#
#
# class Line:
#     def __init__(self, id=None, file=None, tag=None, content=None):
#         self.id = id
#         self.file = file
#         self.tag = tag
#         # self.no = no
#         self.content = content
#
#
# class Diff:
#     def __init__(self, file=None, before_start=None, before_end=None, after_start=None, after_end=None,
#                  context=None, lines=None):
#         self.file = file
#         self.before_start = before_start
#         self.before_end = before_end
#         self.after_start = after_start
#         self.after_end = after_end
#         self.context = context
#         self.lines = lines
#
#     def __repr__(self):
#         lines = f""
#         for line in self.lines:
#             lines = lines + '\n' + line.content
#         return f'{self.file.filename} - {self.file.commit.id}:\n\t' \
#                f'@@ -{self.before_start},{self.before_end} +{self.after_start}, {self.after_end}@@ {self.context}\n' \
#                f'{lines}'
#
#     def __str__(self):
#         lines = f""
#         for line in self.lines:
#             lines = lines + '\n' + line.content
#         return f'{self.file.filename} - {self.file.commit.id}:\n\t' \
#                f'@@ -{self.before_start},{self.before_end} +{self.after_start}, {self.after_end}@@ {self.context}\n' \
#                f'{lines}'
#
#     @classmethod
#     def from_dict(cls, ):
#         # @todo
#         pass
#
#     @classmethod
#     def from_github_dict(cls, file, patch):
#         before_start = before_end = after_start = after_end = context = None
#         patch_lines = patch.splitlines()
#         lines = []
#         for index, patch_line in enumerate(patch_lines):
#             if index == 0:
#                 # Define a regular expression pattern to match the numbers
#                 matches = re.findall(r'@@\s*-(\d+),(\d+)\s*\+(\d+),(\d+)\s*@@\s*(.*)', patch_line)
#                 # Extract the numbers from the match
#                 if matches:
#                     before_start, before_end, after_start, after_end, context = \
#                         int(matches[0][0]), int(matches[0][1]), int(matches[0][2]), int(matches[0][3]), matches[0][4]
#                     print(before_start, before_end, after_start, after_end, context)
#
#             else:
#                 tag, content = Diff.extract_plus_minus(patch_line)
#                 line = Line(index, file, tag, content)
#                 lines.append(line)
#         return cls(file, before_start, before_end, after_start, after_end, context, lines)
#
#     @staticmethod
#     def extract_plus_minus(string):
#         # Define a regular expression pattern to match the desired pattern
#         pattern = r'^([+-])\s(.*)$'
#
#         # Use re.match to check for a match
#         match = re.match(pattern, string)
#
#         if match:
#             # If there's a match, extract the plus or minus sign and the following strings
#             sign = match.group(1)
#             following_strings = match.group(2)
#             return sign, following_strings
#         else:
#             # If there's no match, return an empty string and the original string
#             return '', string
#
#
# class File:
#     def __init__(self, commit=None, filename=None, status=None, diff=None, content=None, file_annotate=None):
#         self.commit = commit
#         self.filename = filename
#         self.status = status
#         self.diff = diff
#         self.content = content
#         self.file_annotate = file_annotate
#
#     def __repr__(self):
#         return f'{self.filename} - {self.status}'
#
#     def __str__(self):
#         return f'{self.filename} - {self.status}'
#
#     @classmethod
#     def from_dict(cls, commit, file_dict):
#         return cls(commit, file_dict['filename'], file_dict['status'], file_dict['contents_url'],
#                    file_dict['patch'])
#
#     @classmethod
#     def from_github_dict(cls, commit, file_dict):
#         return cls(commit, file_dict['filename'], file_dict['status'], file_dict['contents_url'],
#                    file_dict['patch'])
#
#     def get_modified_target_lines(self):
#         modified_target_lines = []
#         for annotate in self.file_annotate.annotates:
#             if self.commit == annotate.commit:
#                 modified_target_lines.append(annotate.target_line)
#         return modified_target_lines
#
#
# class Files:
#     def __init__(self, files=None):
#         self.files = files
#
#     def __iter__(self):
#         for file in self.files:
#             yield file
#
#     def __getitem__(self, index):
#         return self.files[index]
#
#     def __len__(self):
#         return len(self.files)
#
#     def get_file_by_filepath(self, filepath):
#         for file in self.files:
#             if file.filename == filepath:
#                 return file
#         return None
