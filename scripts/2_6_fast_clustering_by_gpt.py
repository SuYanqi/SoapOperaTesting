"""
This is a simple application for sentence embeddings: clustering
Sentences are mapped to sentence embeddings and then agglomerative clustering with a threshold is applied.
"""
from pathlib import Path

from bug_automating.pipelines.constructor import StepClusterer
from bug_automating.utils.file_util import FileUtil
from config import DATA_DIR, APP_NAME_WORDPRESS

if __name__ == "__main__":
    '''
    Error code: 400 - 
    {'error': {'message': "'$.input' is invalid. Please check the API reference: https://platform.openai.com/docs/api-reference.", 'type': 'invalid_request_error', 'param': None, 'code': None}}
    Solution: input cannot be an empty string
              https://platform.openai.com/docs/api-reference/embeddings#:~:text=representing%20the%20input%20text.-,Request%20body,be%202048%20dimensions%20or%20less.%20Example%20Python%20code%20for%20counting%20tokens.,-Show%20possible%20types
    '''
    # https://www.sbert.net/examples/applications/clustering/README.html#agglomerative-clustering
    # https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering
    # reponame = 'firefox'
    # # embedder = SentenceTransformer('all-MiniLM-L6-v2')
    # # embedder = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # maybe this model is better
    # # bugs_filepath = PathUtil.get_filtered_bugs_filepath()
    # # bugs = FileUtil.load_pickle(bugs_filepath)
    # bugs_filepath = Path(DATA_DIR, reponame, "bugs.json")
    # bugs = FileUtil.load_pickle(bugs_filepath)
    #
    # # bugs.merge_steps_by_fast_clustering(embedder)
    # bugs.merge_steps_by_fast_clustering_and_gpt(model="text-embedding-3-large")
    # FileUtil.dump_pickle(bugs_filepath, bugs)

    # app = "firefox"
    # app = "antennapod"
    app = APP_NAME_WORDPRESS

    # test_flag = True
    test_flag = False
    section_foldername = "section"
    step_foldername = "step"
    cluster_foldername = "cluster"
    if test_flag:
        section_foldername = f"test_{section_foldername}"
        step_foldername = f"test_{step_foldername}"
        cluster_foldername = f"test_{cluster_foldername}"
    filepath = Path(DATA_DIR, app, f"{section_foldername}_{step_foldername}_results.json")
    step_splitter_output = FileUtil.load_json(filepath)
    step_clusterer_output = StepClusterer.cluster_steps(step_splitter_output)
    FileUtil.dump_json(Path(DATA_DIR, app, f"{section_foldername}_{step_foldername}_{cluster_foldername}_results.json"),
                       step_clusterer_output)

