from collections import Counter

from bug_automating.utils.nlp_util import NLPUtil
from config import STEP_CLUSTER_THRESHOLD


class GraphUtil:
    INDEX_CLUSTER_DICT = None  # dict() key: cluster_index value: step_cluster
    # dict() key: cluster_index   value: [(bugid, stepid, expected results, Actual results),...]
    INDEX_CLUSTER_EXPECTED_ACTUAL_RESULT_DICT = None
    BUG_ID_BUG_DICT = None  # dict() key: bug_id value: bug (Bug)
    STEP_LIST = None
    STEP_TEXT_LIST = None
    STEP_TEXT_EMBEDDING_LIST = None

    LAYER = "layer"

    @staticmethod
    def get_concepts_name_alias_list(concepts):
        """
        concepts
        [concept0.name, concept0.alias[0], ..., conceptn.name, conceptn.alias[k]]
        """
        step_concepts_list = list()
        if concepts:
            for concept in concepts:
                if concept:
                    step_concepts_list.append(concept.name)
                    if concept.alias:
                        for alia in concept.alias:
                            step_concepts_list.append(alia)
        return step_concepts_list

    @staticmethod
    def get_steps(bugs):
        """
        get step (object) list: GraphUtil.STEP_LIST
        get step_text (string) list: GraphUtil.STEP_TEXT_LIST
        get step_text_embedding (array) list: GraphUtil.STEP_TEXT_EMBEDDING_LIST
        @param bugs: bugs
        @type bugs: object Bugs
        @return: None
        @rtype: None
        """
        step_list = list()
        step_text_list = list()
        for bug in bugs:
            if bug.description.all_steps:
                for step in bug.description.all_steps:
                    step_list.append(step)
                    step_text_list.append(step.text)
        GraphUtil.STEP_LIST = step_list
        GraphUtil.STEP_TEXT_LIST = step_text_list
        GraphUtil.STEP_TEXT_EMBEDDING_LIST = NLPUtil.SBERT_MODEL.encode(step_text_list, convert_to_tensor=True)
        # return step_list, step_text_list

    @staticmethod
    def get_bug_id_bug_dict(bugs):
        """
        get GraphUtil.BUG_ID_BUG_DICT (key: bug.id, value: bug (Bug))
        @param bugs:
        @type bugs: Bugs
        @return: None
        @rtype: None
        """
        GraphUtil.BUG_ID_BUG_DICT = dict()
        for bug in bugs:
            GraphUtil.BUG_ID_BUG_DICT[bug.id] = GraphUtil.BUG_ID_BUG_DICT.get(bug.id, bug)

    @staticmethod
    def get_index_cluster_dict(bugs):
        GraphUtil.INDEX_CLUSTER_DICT = bugs.cluster_index_steps_dict

    @staticmethod
    def get_index_cluster_expected_actual_result_dict():
        """
        NOTE: get GraphUtil.INDEX_CLUSTER_DICT first
        if step is the last step in steps to reproduce, append its (bug_id, step_id, expected result, actual result)
        into GraphUtil.INDEX_CLUSTER_EXPECTED_ACTUAL_RESULT_DICT[cluster_index] (step.cluster_index ==  cluster_index)
        can get GraphUtil.INDEX_CLUSTER_EXPECTED_ACTUAL_RESULT_DICT
        @return: None
        @rtype: None
        """
        GraphUtil.INDEX_CLUSTER_EXPECTED_ACTUAL_RESULT_DICT = dict()
        for cluster_index in GraphUtil.INDEX_CLUSTER_DICT.keys():
            cluster = GraphUtil.INDEX_CLUSTER_DICT[cluster_index]
            # bugid_stepid_expected_actual_result_list = [('BugID', 'No. Step', 'Expected Result', 'Actual Result')]

            if cluster:
                bugid_stepid_expected_actual_result_list = []
                for step in cluster:
                    if step.next_step is None:
                        if step.section_answer.description.expected_results or step.section_answer.description.actual_results:
                            expected_results = None
                            actual_results = None
                            if step.section_answer.description.expected_results:
                                expected_results = (step.section_answer.description.expected_results.text, GraphUtil.get_concepts_name_alias_list(step.section_answer.description.expected_results.concepts))
                            if step.section_answer.description.actual_results:
                                actual_results = (step.section_answer.description.actual_results.text, GraphUtil.get_concepts_name_alias_list(step.section_answer.description.actual_results.concepts))
                            bugid_stepid_expected_actual_result_list.append((step.section_answer.id, step.id,
                                                                             expected_results,
                                                                             actual_results))
                GraphUtil.INDEX_CLUSTER_EXPECTED_ACTUAL_RESULT_DICT[cluster_index] = \
                    GraphUtil.INDEX_CLUSTER_EXPECTED_ACTUAL_RESULT_DICT.get(cluster_index,
                                                                            bugid_stepid_expected_actual_result_list)

    @staticmethod
    def find_clusters_by_element(element):
        cluster_list = list()
        for index, cluster in GraphUtil.INDEX_CLUSTER_DICT.items():
            has_element = False
            for step in cluster:
                for concept in step.concepts_in_target:
                    if element == concept.name:
                        cluster_list.append(cluster)
                        has_element = True
                        break
                if has_element:
                    break
        return cluster_list

    @staticmethod
    def find_clusters_by_cos(text):
        cluster_list = list()
        index_set = set()
        # if not GraphUtil.STEP_TEXT_LIST:
        #     bugs.get_steps()
        embedding1 = NLPUtil.SBERT_MODEL.encode([text], convert_to_tensor=True)
        pairs_list = NLPUtil.get_pairs_with_cossim_by_decreasing(embedding1, GraphUtil.STEP_TEXT_EMBEDDING_LIST)
        for pairs in pairs_list:
            for pair in pairs:
                # {'index': [i, j], 'score': cosine_scores[i][j]}
                if pair['score'] >= STEP_CLUSTER_THRESHOLD:
                    cluster_index = GraphUtil.STEP_LIST[pair['index'][1]].cluster_index
                    index_set.add(cluster_index)
                else:
                    break

        for index in index_set:
            cluster_list.append(GraphUtil.INDEX_CLUSTER_DICT[index])
        return cluster_list

    @staticmethod
    def find_relevant_ranked_bugs_by_bug_id(bugs, bug_id):
        """
        get all relevant bugs of a bug (whose id is bug_id)
        ranking by relevance
        what is relevance:
            a. the number of steps in the same cluster (the same step.cluster_index)
            b. if a is the same, the bug with the smaller sum of cluster_index_count (like df, the number of times cluster_index appears in different bugs) is ranked higher
            c. sort by bug.creation_time (reverse=True)
            # d. more same elements (Concept object)
        @param bugs: bugs
        @type bugs: Bugs
        @param bug_id: the id of bug
        @type bug_id: int
        @return: bug list (ranked by relevance of the bug)
        @rtype: list
        """
        bug_list = list()
        # key: cluster_index   value: count (number of cluster occurs in different bugs, like df)
        cluster_index_count_dict = dict()
        # key: bug      value: [cluster_index, cluster_index, ...]
        bug_cluster_index_list_dict = dict()
        # for concept ranking **************************************************************************
        # key: bug      value: [concept_]
        # bug_concept_list_dict = dict()
        # ***********************************************************************************************
        """
        key: bug
        value: ([cluster_index, cluster_index, ...], cluster_index_count_sum)
                "cluster_index_list": [cluster_index, cluster_index, ...]
                cluster_index_count_sum: sum of cluster_index_df
        """
        bug_ranking_details_dict = dict()

        # find input_bug
        input_bug = None
        for bug in bugs:
            if bug.id == bug_id:
                input_bug = bug
                break
        # initiate cluster_index_count_dict (key: cluster_index   value: count (like df))
        # get bug_cluster_dict (key: bug      value: [cluster_index, cluster_index, ...])
        if input_bug:
            for input_bug_step in input_bug.description.all_steps:
                cluster_index = input_bug_step.cluster_index
                cluster_index_count_dict[cluster_index] = cluster_index_count_dict.get(cluster_index, 0)
                cluster = GraphUtil.INDEX_CLUSTER_DICT[cluster_index]
                for step in cluster:
                    if step.section_answer.id != input_bug.id:
                        bug_cluster_index_list_dict[step.section_answer] = bug_cluster_index_list_dict.get(step.section_answer, [])
                        bug_cluster_index_list_dict[step.section_answer].append(cluster_index)
        # assign values to cluster_index_count_dict
        for bug in bug_cluster_index_list_dict.keys():
            for cluster_index in cluster_index_count_dict.keys():
                if cluster_index in bug_cluster_index_list_dict[bug]:
                    cluster_index_count_dict[cluster_index] = cluster_index_count_dict[cluster_index] + 1
            # print(f"{bug.id}: {bug_cluster_index_list_dict[bug]}")
        # for cluster_index in cluster_index_count_dict.keys():
        # print(f"{cluster_index}: {cluster_index_count_dict[cluster_index]}")

        # ranking rules
        # sort bugs by number of steps in the same cluster
        cluster_index_list_len_bug_list_dict = dict()  # key: cluster_index_list_len, value: (bug, sum)_list
        # sum: the sum of cluster_index_count
        for bug in sorted(bug_cluster_index_list_dict,
                          key=lambda k: len(bug_cluster_index_list_dict[k]), reverse=True):
            cluster_index_list_len_bug_list_dict[len(bug_cluster_index_list_dict[bug])] = \
                cluster_index_list_len_bug_list_dict.get(len(bug_cluster_index_list_dict[bug]), [])
            cluster_index_df_sum = 0
            for cluster_index in bug_cluster_index_list_dict[bug]:
                cluster_index_df_sum = cluster_index_df_sum + cluster_index_count_dict[cluster_index]
            """
            if want to add concept ranking:
            (bug, cluster_index_df_sum) -> (bug, cluster_index_df_sum, concept_count, concept_df_sum)
            """
            cluster_index_list_len_bug_list_dict[len(bug_cluster_index_list_dict[bug])].append((bug,
                                                                                                cluster_index_df_sum))
            # print(bug)
        # sort bugs by the sum of cluster_index_count (like df) (Ascending)
        for cluster_index_list_len in cluster_index_list_len_bug_list_dict.keys():
            # print(f"{cluster_index_list_len}: ")
            """
            if want to add concept ranking:
            key=lambda x: x[1] -> key=lambda x: (x[1], x[2], x[3])
            """
            # cluster_index_list_len_bug_list_dict[cluster_index_list_len] = \
            #     sorted(cluster_index_list_len_bug_list_dict[cluster_index_list_len], key=lambda x: x[1])
            temp_bug_list = list()
            for bug, cluster_index_df_sum in cluster_index_list_len_bug_list_dict[cluster_index_list_len]:
                # print(f"\t\t{bug.id}: {cluster_index_df_sum}")
                temp_bug_list.append((-cluster_index_df_sum,
                                      bug))  # smaller cluster_index_df_sum, higher ranking, for reverse sorting, get the -cluster_index_df_sum
                # bug_list.append(bug)
            """
            sorted by:
            1. -cluster_index_df_sum
            2. bug.creation_time
            """
            temp_bug_list = sorted(temp_bug_list, key=lambda x: (x[0], x[1].creation_time), reverse=True)
            for _, bug in temp_bug_list:
                bug_list.append(bug)
        # get bug_ranking_details_dict
        for bug in bug_list:
            cluster_index_count_sum = 0
            for cluster_index in bug_cluster_index_list_dict[bug]:
                cluster_index_count_sum = cluster_index_count_sum + cluster_index_count_dict[cluster_index]

            bug_ranking_details_dict[bug] = bug_ranking_details_dict.get(bug, (bug_cluster_index_list_dict[bug],
                                                                               cluster_index_count_sum))
        # print(bug_ranking_details_dict)

        return bug_list, bug_ranking_details_dict

    @staticmethod
    def find_relevant_ranked_bugs_by_bug_id_with_step_type(bugs, bug_id):
        """
        get all relevant bugs of a bug (whose id is bug_id)
        ranking by relevance
        what is relevance:
            a. the number of steps in the same cluster (the same step.cluster_index)
            b. if a is the same, the bug with the smaller sum of cluster_index_count (like df, the number of times cluster_index appears in different bugs) is ranked higher
            c. sort by bug.creation_time (reverse=True)
            # d. more same elements (Concept object)
        @param bugs: bugs
        @type bugs: Bugs
        @param bug_id: the id of bug
        @type bug_id: int
        @return: bug list (ranked by relevance of the bug)
        @rtype: list
        """
        bug_list = list()
        # key: cluster_index   value: count (number of cluster occurs in different bugs, like df)
        cluster_index_count_dict = dict()
        # key: bug      value: [cluster_index, cluster_index, ...]
        bug_cluster_index_list_dict = dict()
        # for concept ranking **************************************************************************
        # key: bug      value: [concept_]
        # bug_concept_list_dict = dict()
        # ***********************************************************************************************
        """
        key: bug
        value: ([cluster_index, cluster_index, ...], cluster_index_count_sum)
                "cluster_index_list": [cluster_index, cluster_index, ...]
                cluster_index_count_sum: sum of cluster_index_df
        """
        bug_ranking_details_dict = dict()

        # find input_bug
        input_bug = None
        for bug in bugs:
            if bug.id == bug_id:
                input_bug = bug
                break
        # initiate cluster_index_count_dict (key: cluster_index   value: count (like df))
        # get bug_cluster_dict (key: bug      value: [cluster_index, cluster_index, ...])
        if input_bug:
            # for input_bug_step in input_bug.description.steps_to_reproduce:
            scenario = input_bug.description.scenarios[0]
            for input_bug_step in scenario.steps:
                # if input_bug_step.is_operational:
                cluster_index = input_bug_step.cluster_index
                cluster_index_count_dict[cluster_index] = cluster_index_count_dict.get(cluster_index, 0)
                cluster = GraphUtil.INDEX_CLUSTER_DICT[cluster_index]
                for step in cluster:
                    if step.bug.id != input_bug.id:
                        bug_cluster_index_list_dict[step.bug] = bug_cluster_index_list_dict.get(step.bug, [])
                        bug_cluster_index_list_dict[step.bug].append(cluster_index)
        # assign values to cluster_index_count_dict
        for bug in bug_cluster_index_list_dict.keys():
            for cluster_index in cluster_index_count_dict.keys():
                if cluster_index in bug_cluster_index_list_dict[bug]:
                    cluster_index_count_dict[cluster_index] = cluster_index_count_dict[cluster_index] + 1
            # print(f"{bug.id}: {bug_cluster_index_list_dict[bug]}")
        # for cluster_index in cluster_index_count_dict.keys():
        # print(f"{cluster_index}: {cluster_index_count_dict[cluster_index]}")

        # ranking rules
        # sort bugs by number of steps in the same cluster
        cluster_index_list_len_bug_list_dict = dict()  # key: cluster_index_list_len, value: (bug, sum)_list
        # sum: the sum of cluster_index_count
        for bug in sorted(bug_cluster_index_list_dict,
                          key=lambda k: len(bug_cluster_index_list_dict[k]), reverse=True):
            cluster_index_list_len_bug_list_dict[len(bug_cluster_index_list_dict[bug])] = \
                cluster_index_list_len_bug_list_dict.get(len(bug_cluster_index_list_dict[bug]), [])
            cluster_index_df_sum = 0
            for cluster_index in bug_cluster_index_list_dict[bug]:
                cluster_index_df_sum = cluster_index_df_sum + cluster_index_count_dict[cluster_index]
            """
            if want to add concept ranking:
            (bug, cluster_index_df_sum) -> (bug, cluster_index_df_sum, concept_count, concept_df_sum)
            """
            cluster_index_list_len_bug_list_dict[len(bug_cluster_index_list_dict[bug])].append((bug,
                                                                                                cluster_index_df_sum))
            # print(bug)
        # sort bugs by the sum of cluster_index_count (like df) (Ascending)
        for cluster_index_list_len in cluster_index_list_len_bug_list_dict.keys():
            # print(f"{cluster_index_list_len}: ")
            """
            if want to add concept ranking:
            key=lambda x: x[1] -> key=lambda x: (x[1], x[2], x[3])
            """
            # cluster_index_list_len_bug_list_dict[cluster_index_list_len] = \
            #     sorted(cluster_index_list_len_bug_list_dict[cluster_index_list_len], key=lambda x: x[1])
            temp_bug_list = list()
            for bug, cluster_index_df_sum in cluster_index_list_len_bug_list_dict[cluster_index_list_len]:
                # print(f"\t\t{bug.id}: {cluster_index_df_sum}")
                temp_bug_list.append((-cluster_index_df_sum,
                                      bug))  # smaller cluster_index_df_sum, higher ranking, for reverse sorting, get the -cluster_index_df_sum
                # bug_list.append(bug)
            """
            sorted by:
            1. -cluster_index_df_sum
            2. bug.creation_time
            """
            temp_bug_list = sorted(temp_bug_list, key=lambda x: (x[0], x[1].creation_time), reverse=True)
            for _, bug in temp_bug_list:
                bug_list.append(bug)
        # get bug_ranking_details_dict
        for bug in bug_list:
            cluster_index_count_sum = 0
            for cluster_index in bug_cluster_index_list_dict[bug]:
                cluster_index_count_sum = cluster_index_count_sum + cluster_index_count_dict[cluster_index]

            bug_ranking_details_dict[bug] = bug_ranking_details_dict.get(bug, (bug_cluster_index_list_dict[bug],
                                                                               cluster_index_count_sum))
        # print(bug_ranking_details_dict)

        return bug_list, bug_ranking_details_dict

    @staticmethod
    def get_test_reports_from_two_bugs(bug1, bug2):
        """
        generate test reports from two bugs

        @param bug1:
        @type bug1: Bug
        @param bug2:
        @type bug2: Bug
        @return:
        @rtype:
        """
        test_report_dict_list = list()
        test_report_dict_from_bug1_bug2 = GraphUtil.get_test_reports_by_merging_two_bugs(bug1, bug2)
        if test_report_dict_from_bug1_bug2:
            test_report_dict_list.append(test_report_dict_from_bug1_bug2)
        test_report_dict_from_bug2_bug1 = GraphUtil.get_test_reports_by_merging_two_bugs(bug2, bug1)
        if test_report_dict_from_bug2_bug1:
            test_report_dict_list.append(test_report_dict_from_bug2_bug1)

        for step1 in bug1.description.all_steps:
            for step2 in bug2.description.all_steps:
                if step1.cluster_index == step2.cluster_index:
                    test_report_dict = GraphUtil.get_test_reports_by_two_steps(step1, step2)
                    test_report_dict_list.append(test_report_dict)
                    test_report_dict = GraphUtil.get_test_reports_by_two_steps(step2, step1)
                    test_report_dict_list.append(test_report_dict)
        return test_report_dict_list

    @staticmethod
    def get_test_reports_by_merging_two_bugs(bug1, bug2):
        """
        merge two bugs to get test report:
        for steps1 in bug1, steps2 in bug2
        return precondition1 steps1 + steps2 result2
        @param bug1:
        @type bug1:
        @param bug2:
        @type bug2:
        @return:
        @rtype:
        """
        test_report_dict = {
            # 'id': None,
            # 'Summary': None,
            'Preconditions': None,
            'PreconditionsElements': None,
            'StepsToReproduce': None,
            'ExpectedResults': None,
            'ExpectedResultsElements': None,
            'ActualResults': None,
            'ActualResultsElements': None,
            'Notes': None,
            'NotesElements': None,
            'SeeAlso': None,
            # 'Attachments':
        }
        if bug1.description.prerequisites:
            test_report_dict['Preconditions'] = bug1.description.prerequisites.text
            test_report_dict['PreconditionsElements'] = GraphUtil.get_concepts_name_alias_list(bug1.description.prerequisites.concepts)
        bug1_step_list = list()
        for step in bug1.description.all_steps:
            bug1_step_list.append(GraphUtil.get_step_dict(step))
        bug2_step_list = list()
        for step in bug2.description.all_steps:
            bug2_step_list.append(GraphUtil.get_step_dict(step))
        test_report_dict['StepsToReproduce'] = bug1_step_list + bug2_step_list

        if bug2.description.expected_results:
            test_report_dict['ExpectedResults'] = bug2.description.expected_results.text
            test_report_dict['ExpectedResultsElements'] = GraphUtil.get_concepts_name_alias_list(bug2.description.expected_results.concepts)
        if bug2.description.actual_results:
            test_report_dict['ActualResults'] = bug2.description.actual_results.text
            test_report_dict['ActualResultsElements'] = GraphUtil.get_concepts_name_alias_list(bug2.description.actual_results.concepts)
        if bug2.description.notes:
            test_report_dict['Notes'] = bug2.description.notes.text
            test_report_dict['NotesElements'] = GraphUtil.get_concepts_name_alias_list(bug2.description.notes.concepts)
        return test_report_dict

    @staticmethod
    def get_test_reports_by_two_steps(step1, step2):
        """

        @param step1:
        @type step1: Step
        @param step2:
        @type step2: Step
        @return:
        @rtype:
        """
        test_report_dict = {
            # 'id': None,
            # 'Summary': None,
            'Preconditions': None,
            'PreconditionsElements': None,
            'StepsToReproduce': None,
            'ExpectedResults': None,
            'ExpectedResultsElements': None,
            'ActualResults': None,
            'ActualResultsElements': None,
            'Notes': None,
            'NotesElements': None,
            'SeeAlso': None,
            # 'Attachments':
        }
        if step1.section_answer.description.prerequisites:
            test_report_dict['Preconditions'] = step1.section_answer.description.prerequisites.text
            test_report_dict['PreconditionsElements'] = GraphUtil.get_concepts_name_alias_list(step1.section_answer.description.prerequisites.concepts)

        prev_step1 = step1
        prev_step1_list = list()
        while prev_step1:
            # prev_step1_list.append(prev_step1.text)
            # print(prev_step1)
            # prev_step1_dict = GraphUtil.get_step_dict((prev_step1.cluster_index,
            #                                            prev_step1.text,
            #                                            GraphUtil.INDEX_CLUSTER_EXPECTED_ACTUAL_RESULT_DICT[
            #                                                prev_step1.cluster_index]))
            prev_step1_dict = GraphUtil.get_step_dict(prev_step1)
            # print(prev_step1_dict)
            prev_step1_list.append(prev_step1_dict)
            prev_step1 = prev_step1.prev_step
        prev_step1_list.reverse()  # reverse the order of list elements
        next_step2 = step2
        next_step2_list = list()

        while next_step2:
            next_step2 = next_step2.next_step
            if next_step2:
                # next_step2_list.append(next_step2.text)
                # next_step2_dict = GraphUtil.get_step_dict((next_step2.cluster_index,
                #                                            next_step2.text,
                #                                            GraphUtil.INDEX_CLUSTER_EXPECTED_ACTUAL_RESULT_DICT[
                #                                                next_step2.cluster_index]))
                next_step2_dict = GraphUtil.get_step_dict(next_step2)
                next_step2_list.append(next_step2_dict)
        test_report_dict['StepsToReproduce'] = prev_step1_list + next_step2_list
        if step2.section_answer.description.expected_results:
            test_report_dict['ExpectedResults'] = step2.section_answer.description.expected_results.text
            test_report_dict['ExpectedResultsElements'] = GraphUtil.get_concepts_name_alias_list(step2.section_answer.description.expected_results.concepts)
        if step2.section_answer.description.actual_results:
            test_report_dict['ActualResults'] = step2.section_answer.description.actual_results.text
            test_report_dict['ActualResultsElements'] = GraphUtil.get_concepts_name_alias_list(step2.section_answer.description.actual_results.concepts)
        if step2.section_answer.description.notes:
            test_report_dict['Notes'] = step2.section_answer.description.notes.text
            test_report_dict['NotesElements'] = GraphUtil.get_concepts_name_alias_list(step2.section_answer.description.notes.concepts)
        return test_report_dict

    # @staticmethod
    # def get_see_also_from_test_report_dict(test_report_dict):
    #     see_also = list()
    #     for step in test_report_dict["StepsToReproduce"]:
    #         if step[""]:

    @staticmethod
    def get_next_clusters(cluster):
        """
        get cluster's next one layer clusters
        @param cluster:
        @type cluster:
        @return: cluster_list
        @rtype: list
        """
        index_set = set()
        cluster_list = list()
        for step in cluster:
            if step.next_step:
                index_set.add(step.next_step.cluster_index)

        for index in index_set:
            cluster_list.append(GraphUtil.INDEX_CLUSTER_DICT[index])
        return cluster_list

    @staticmethod
    def get_next_clusters_by_bfs(cluster):
        """
        get all next clusters (all layers) by using Breadth-first search (BFS)
        @param cluster: the start node
        @type cluster: step list
        @return: next_clusters (clusters splitted by GraphUtil.LAYER)
        @rtype: list [cluster, GraphUtil.LAYER, cluster, cluster, GraphUtil.LAYER, cluster, cluster]
        """
        visited = []
        queue = []
        next_clusters = []

        visited.append(cluster)
        queue.append(cluster)
        queue.append(GraphUtil.LAYER)

        while queue:
            s = queue.pop(0)
            if s == GraphUtil.LAYER:
                next_clusters.append(GraphUtil.LAYER)
                if queue and queue[-1] != GraphUtil.LAYER:
                    queue.append(GraphUtil.LAYER)
                continue
            next_clusters.append(s)
            # print(s, end=" ")
            for neighbour in GraphUtil.get_next_clusters(s):
                if neighbour not in visited:
                    visited.append(neighbour)
                    queue.append(neighbour)
        return next_clusters

    # @staticmethod
    # def get_step_dict(step):
    #     """
    #     get step dict
    #     @param step: (cluster_index, step_text, [(bugid, stepid, expected results, Actual results),...])
    #     @type step: tuple
    #     @return: step_dict
    #     @rtype: dict
    #     """
    #     expected_actual_result_list = step[2]
    #     expected_actual_result_dict_list = list()
    #
    #     for expected_actual_result in expected_actual_result_list:
    #         expected_actual_result_dict = {
    #             'BugId': expected_actual_result[0],
    #             'StepId': expected_actual_result[1],
    #             'ExpectedResults': expected_actual_result[2],
    #             'ActualResults': expected_actual_result[3]
    #         }
    #         expected_actual_result_dict_list.append(expected_actual_result_dict)
    #     step_dict = {
    #         'ClusterIndex': step[0],
    #         'StepText': step[1],
    #         'ExpectedActualResultsDictList': expected_actual_result_dict_list,
    #     }
    #     return step_dict

    @staticmethod
    def get_step_dict(step):
        """
        get step dict
        @param step: (cluster_index, step_text, [(bugid, stepid, expected results, Actual results),...])
        @type step: tuple
        @return: step_dict
        @rtype: dict
        """
        expected_actual_result_list = GraphUtil.INDEX_CLUSTER_EXPECTED_ACTUAL_RESULT_DICT[step.cluster_index]
        expected_actual_result_dict_list = list()
        for expected_actual_result in expected_actual_result_list:
            expected_actual_result_dict = {
                'BugId': expected_actual_result[0],
                'StepId': expected_actual_result[1],
                'ExpectedResults': expected_actual_result[2][0],
                'ExpectedResultsElements': expected_actual_result[2][1],
                'ActualResults': expected_actual_result[3][0],
                'ActualResultsElements': expected_actual_result[3][1]
            }
            expected_actual_result_dict_list.append(expected_actual_result_dict)
        # element_dict_list = list()
        # for element in step.concepts:
        #     element_dict = {
        #         'name': element.name,
        #         'category': element.category,
        #         'alias': element.alias,
        #         'related_elements': element.related_concepts,
        #     }
        #     element_dict_list.append(element_dict)
        # action_dict = {
        #     'name': step.action,
        #     'standard_name': step.action_object.name,
        #     'category': step.action_object.category,
        #     'equivalent': step.action_object.equivalent,
        #     'opposite': step.action_object.opposite,
        #     'alias': step.action_object.alias,
        # }
        step_concepts_list = GraphUtil.get_concepts_name_alias_list(step.concepts)
        # print(step_concepts_list)
        step_dict = {
            'ClusterIndex': step.cluster_index,
            'StepText': step.text,
            'StepElements': step_concepts_list,
            'ExpectedActualResultsDictList': expected_actual_result_dict_list,
            # 'Action': action_dict,
            # 'ElementList': element_dict_list,

        }

        return step_dict

    @staticmethod
    def get_bug_dict(bug):
        """
        get bug dict
        @param bug:
        @type bug:
        @return:
        @rtype:
        """
        bug_dict = {
            'id': None,
            'product': None,
            'component': None,
            'Summary': None,
            'Preconditions': None,
            'PreconditionsElements': None,
            'StepsToReproduce': None,
            'ExpectedResults': None,
            'ExpectedResultsElements': None,
            'ActualResults': None,
            'ActualResultsElements': None,
            'Notes': None,
            'NotesElements': None,
            'Attachments': None,
            # only for relevant bug report
            # 'cluster_index_list': None,
            # 'cluster_index_count_sum': None,
            # 'bugReport': None,
        }
        if bug.id:
            bug_dict['id'] = bug.id
        if bug.product_component_pair.product:
            bug_dict['product'] = bug.product_component_pair.product
        if bug.product_component_pair.component:
            bug_dict['component'] = bug.product_component_pair.component
        if bug.summary:
            bug_dict['Summary'] = bug.summary
        if bug.description.prerequisites:
            bug_dict['Preconditions'] = bug.description.prerequisites.text
            bug_dict['PreconditionsElements'] = GraphUtil.get_concepts_name_alias_list(bug.description.prerequisites.concepts)
        if bug.description.all_steps:
            steps = list()
            for index, step in enumerate(bug.description.all_steps):
                # step_dict = {
                #     "step_id": index,
                #     "step_text": step.text
                # }

                # steps.append(GraphUtil.get_step_dict((step.cluster_index,
                #                                       step.text,
                #                                       GraphUtil.INDEX_CLUSTER_EXPECTED_ACTUAL_RESULT_DICT[
                #                                           step.cluster_index])))
                steps.append(GraphUtil.get_step_dict(step))
                # steps.append(step.text)
            bug_dict['StepsToReproduce'] = steps
        if bug.description.expected_results:
            bug_dict['ExpectedResults'] = bug.description.expected_results.text
            bug_dict['ExpectedResultsElements'] = GraphUtil.get_concepts_name_alias_list(bug.description.expected_results.concepts)
        if bug.description.actual_results:
            bug_dict['ActualResults'] = bug.description.actual_results.text
            bug_dict['ActualResultsElements'] = GraphUtil.get_concepts_name_alias_list(bug.description.actual_results.concepts)
        if bug.description.notes:
            bug_dict['Notes'] = bug.description.notes.text
            bug_dict['NotesElements'] = GraphUtil.get_concepts_name_alias_list(bug.description.notes.concepts)
        if bug.attachments:
            bug_dict['Attachments'] = []
            for attachment in bug.attachments:
                attachment_dict = {
                    "file_name": attachment.filepath,
                    "type": attachment.content_type.split("/")[0],
                    "content_type": attachment.content_type,
                    "attachment_url": attachment.url,
                }
                if attachment_dict["type"] == "video" or attachment_dict["type"] == "image":
                    bug_dict['Attachments'].append(attachment_dict)
        # if ranking_details:
        #     bug_dict['cluster_index_list'] = ranking_details[0]
        #     bug_dict['cluster_index_count_sum'] = ranking_details[1]
        # bug_dict['bug_report'] = {
        #     'id': bug_dict['id'],
        #     'Summary': bug_dict['Summary'],
        #     'Preconditions': bug_dict['Preconditions'],
        #     'StepsToReproduce': bug_dict['StepsToReproduce'],
        #     'ExpectedResults': bug_dict['ExpectedResults'],
        #     'ActualResults': bug_dict['ActualResults'],
        #     'Notes': bug_dict['Notes'],
        #     'Attachments': bug_dict['Attachments'],
        # }
        return bug_dict

    @staticmethod
    def get_relevant_bug_dict(bug, ranking_details=None):
        """
        get relevant bug dict
        @param ranking_details: ([cluster_index, cluster_index, ...], cluster_index_count_sum)
                                                 "cluster_index_list": [cluster_index, cluster_index, ...]
                                                 cluster_index_count_sum: sum of cluster_index_df
        @type ranking_details: (, )
        @param bug:
        @type bug:
        @return:
        @rtype:
        """
        relevant_bug_dict = {
            'id': None,
            'Summary': None,
            # only for relevant bug report
            'cluster_index_list': None,
            'cluster_index_count_sum': None,
            'bugReport': None,
        }
        bug_dict = GraphUtil.get_bug_dict(bug)
        if bug.id:
            relevant_bug_dict['id'] = bug.id
        if bug.summary:
            relevant_bug_dict['Summary'] = bug.summary
        if ranking_details:
            cluster_index_list = ranking_details[0]
            cluster_index_count_dict = Counter(cluster_index_list)
            cluster_index_count_list = [[cluster_index, count]
                                        for cluster_index, count in cluster_index_count_dict.items()]
            relevant_bug_dict['cluster_index_list'] = cluster_index_count_list
            relevant_bug_dict['cluster_index_count_sum'] = ranking_details[1]
        relevant_bug_dict['bugReport'] = bug_dict
        return relevant_bug_dict
