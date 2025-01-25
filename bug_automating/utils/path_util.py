from pathlib import Path

from config import DATA_DIR, OUTPUT_DIR


class PathUtil:

    @staticmethod
    def get_bugs_filepath(reponame, filename="bugs"):
        return Path(DATA_DIR, reponame, f"{filename}.json")

    @staticmethod
    def get_commits_filepath(reponame, filename="commits"):
        return Path(DATA_DIR, reponame, f"{filename}.json")

    @staticmethod
    def get_files_filepath(reponame, filename="files"):
        return Path(DATA_DIR, reponame, f"{filename}.json")

    @staticmethod
    def get_specific_commit_id_repo_filepath(commit_id, reponame="WordPress-Android"):
        return Path(DATA_DIR, reponame, "repos", f"{reponame}-{commit_id}")

    @staticmethod
    def get_test_scenario_extractor_output(reponame, filename="scenario_extractor_output",
                                           with_instances=True, with_cots=False):
        if with_instances:
            filename = filename + "_with_instances"
        if with_cots:
            filename = filename + "_with_cots"
        return Path(DATA_DIR, reponame, f"{filename}.json")

    @staticmethod
    def get_step_splitter_output(reponame, filename="step_splitter_output",
                                 with_instances=True, with_cots=False):
        if with_instances:
            filename = filename + "_with_instances"
        if with_cots:
            filename = filename + "_with_cots"
        return Path(DATA_DIR, reponame, f"{filename}.json")

    @staticmethod
    def get_step_clusterer_output(reponame, filename="step_clusterer_output"):
        # if with_instances:
        #     filename = filename + "_with_instances"
        # if with_cots:
        #     filename = filename + "_with_cots"
        return Path(DATA_DIR, reponame, f"{filename}.json")
