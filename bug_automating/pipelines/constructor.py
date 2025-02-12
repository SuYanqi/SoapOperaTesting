import copy
import json
import logging

from tqdm import tqdm
from sentence_transformers import util

from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.list_util import ListUtil
from bug_automating.utils.llm_util import LLMUtil
from config import STEP_MERGE_THRESHOLD, SYNC_EMBEDDING_NUM, STEP_CLUSTER_THRESHOLD


class StepSplitter:
    def __init__(self):
        pass

    # split STR into Steps **********************************************************
    @staticmethod
    def convert_instances_into_qa_pairs(bugs=None, with_step_type=False):
        qa_pairs = []
        if with_step_type:
            instances = Placeholder.STEP_SPLITTER_INSTANCES_WITH_TYPE
        else:
            instances = Placeholder.STEP_SPLITTER_INSTANCES
        if instances:
            for instance_dict in instances:
                # bug = bugs.get_bug_by_id(int(instance_dict['bug_id']))
                question = StepSplitter.question_for_step_splitting(instance_dict[Placeholder.STEPS_TO_REPRODUCE])
                answer = StepSplitter.answer_for_step_splitting(instance_dict['output'])
                # answer = instance_dict['output']
                # answer = json.loads(answer)
                # print(answer)
                # print(type(answer))
                qa_pairs.append((question, answer))
        return qa_pairs

    @staticmethod
    def get_session_prompt(with_step_type=False):
        session_prompt = f"I am a step splitter. " \
                         f"I can split 'Steps To Reproduce' section into steps, " \
                         f"which each step is an individual UI operation."
        if with_step_type:
            session_prompt = session_prompt + \
                             f'\nMeanwhile, I can classify each step into ' \
                             f'{Placeholder.OPERATION} or {Placeholder.NON_OPERATION}.'
        return session_prompt

    @staticmethod
    def get_initial_messages(bugs=None, with_step_type=False):
        session_prompt = StepSplitter.get_session_prompt(with_step_type)
        qa_pairs = None
        if bugs:
            qa_pairs = StepSplitter.convert_instances_into_qa_pairs(bugs, with_step_type)
        messages = LLMUtil.get_messages(session_prompt, qa_pairs)
        return messages

    @staticmethod
    def question_for_step_splitting(bug=None):
        return f"{Placeholder.STEPS_TO_REPRODUCE}: {bug}\n\n" \
               f"Please split {Placeholder.STEPS_TO_REPRODUCE} into steps, " \
               f"especially splitting the step with multiple UI operations into steps with one UI operation). " \
               "Please answer in the json format: [{'STEP': '', 'STEP_TYPE': 'OPERATION'}," \
               "{'STEP': '', 'STEP_TYPE': 'NON_OPERATION'},]"
        # f"Please be careful not to exceed the given scope of the content."

    @staticmethod
    def answer_for_step_splitting(outputs, chains=None):
        if chains:
            return f"Chains-of-Thought: {chains}\n\n" \
                   f"Outputs: {outputs}"
        return json.dumps(outputs)

    @staticmethod
    def split_s2r(bug=None, bugs=None, with_step_type=False):
        # if messages is None:
        messages = StepSplitter.get_initial_messages(bugs, with_step_type)
        # extract summary
        question = StepSplitter.question_for_step_splitting(bug)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question, messages)
        # print(self.summary_question)
        # input()
        answer, cost = LLMUtil.ask_llm_for_chat_completions(messages, model=LLMUtil.GPT4O_MINI_NAME, temperature=0.2)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_ASSISTANT, answer, messages)

        LLMUtil.show_messages(messages)
        # print(messages)
        print(cost)
        # desc_question, desc_answer = LLMUtil.question_answer(self.desc_question)
        # print(summary_question)
        # print(summary_answer)
        # print(desc_question)
        # print(desc_answer)
        # answer = Answer.from_answer(summary_pair, summary_answer, desc_answer)
        # raw_answer = RawAnswer(summary_pair,
        #                        QA(self.summary_question, summary_answer),
        #                        QA(self.desc_question, desc_answer))

        return answer, messages, cost


class SecSplitter:
    def __init__(self):
        pass

    @staticmethod
    def convert_instances_into_qa_pairs(bugs=None):
        qa_pairs = []
        if Placeholder.SEC_SPLITTER_INSTANCES:
            for instance_dict in Placeholder.SEC_SPLITTER_INSTANCES:
                # bug = bugs.get_bug_by_id(int(instance_dict['bug_id']))
                question = SecSplitter.question_for_sec_splitting(instance_dict['summary'],
                                                                  instance_dict['description'])
                answer = SecSplitter.answer_for_sec_splitting(instance_dict['output'])
                qa_pairs.append((question, answer))
        return qa_pairs

    @staticmethod
    def get_session_prompt():
        session_prompt = f"I am a text splitter. " \
                         f"I can split the text into the specific parts."
        return session_prompt

    @staticmethod
    def get_initial_messages(bugs=None):
        session_prompt = SecSplitter.get_session_prompt()
        qa_pairs = None
        if bugs:
            qa_pairs = SecSplitter.convert_instances_into_qa_pairs(bugs)
        messages = LLMUtil.get_messages(session_prompt, qa_pairs)
        return messages

    @staticmethod
    def question_for_sec_splitting(summary, description):
        return f"Bug Summary: {summary}\n" \
               f"Bug Description:\n{description}\n\n" \
               f"Please split the bug description into the specific sections " \
               "and answer in the format of a JSON string: " \
               "{" \
               f'"{Placeholder.PRECONDITIONS}":["",],' \
               f'"{Placeholder.STEPS_TO_REPRODUCE}":["",],' \
               f'"{Placeholder.EXPECTED_RESULTS}":["",],' \
               f'"{Placeholder.ACTUAL_RESULTS}":["",],' \
               f'"{Placeholder.NOTES}":["",],' \
               f'"{Placeholder.AFFECTED_VERSIONS}":["",],' \
               f'"{Placeholder.AFFECTED_PLATFORMS}":["",],' \
               f'"{Placeholder.OTHERS}":["",]' \
               "}"

    @staticmethod
    def answer_for_sec_splitting(outputs):
        return json.dumps(outputs)

    @staticmethod
    def split_section(bug, bugs=None, model=LLMUtil.GPT4O_MINI_NAME):
        messages = SecSplitter.get_initial_messages(bugs)
        # extract summary
        question = SecSplitter.question_for_sec_splitting(bug.summary, bug.description.text)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question, messages)
        # print(self.summary_question)
        # input()
        answer, total_cost = LLMUtil.ask_llm_for_chat_completions(messages, model)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_ASSISTANT, answer, messages)

        # LLMUtil.show_messages(messages)
        # desc_question, desc_answer = LLMUtil.question_answer(self.desc_question)
        # answer = Answer.from_answer(summary_pair, summary_answer, desc_answer)
        # raw_answer = RawAnswer(summary_pair,
        #                        QA(self.summary_question, summary_answer),
        #                        QA(self.desc_question, desc_answer))

        return answer, messages, total_cost

    @staticmethod
    def get_messages_list_for_bugs(bugs, with_instances=False):
        initial_messages = SecSplitter.get_initial_messages(with_instances)
        # print(initial_messages)
        messages_list = []
        for bug in tqdm(bugs, ascii=True):
            question = SecSplitter.question_for_sec_splitting(bug)
            # print(question)
            # for initial_message in initial_messages:
            #     print(initial_message)
            # print("******************")
            # print(initial_messages)
            messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question,
                                                                   copy.deepcopy(initial_messages))
            # for message in messages:
            #     print(message)
            messages_list.append(messages)
            # print("############################")
        return messages_list


# class StepCluster:
#     @staticmethod
#     def merge_steps_by_fast_clustering_and_gpt(step_text_list, model="text-embedding-3-large"):
#         """
#         https://www.sbert.net/examples/applications/clustering/README.html
#         Fast Clustering
#         ** cannot be an empty string for openai embedding **
#         merge steps:
#         # 1. Merge steps by concepts (if concepts_in_target and action_object)
#         2. Merge steps by fast clustering
#         3. Get self.step_index_cluster_dict and assign index for Step.cluster_index
#
#         @param model: SBERT
#         @type model: sentence embedding
#         @return: self.step_index_cluster_dict, Step.cluster_index
#         @rtype: dict{ key: index, value: cluster ((set(step(object), step(object), ...))}), int (index)
#         """
#         clusters = list()
#         # step_list, step_text_list = self.get_steps()
#         logging.warning("Cluster steps by Fast Clustering...")
#         step_index_set = set()
#         # # (score, i, j) list
#         # step_embeddings = model.encode(step_text_list, batch_size=SBERT_BATCH_SIZE, show_progress_bar=True,
#         #                                convert_to_tensor=True)
#         # # step_embeddings = FileUtil.load_pickle(Path(DATA_DIR, 'step_embeddings.json'))
#         # # FileUtil.dump_pickle(Path(DATA_DIR, 'step_embeddings.json'), step_embeddings)
#         # step_embeddings = step_embeddings.to('cpu')
#         step_embeddings = []
#         logging.warning("Step embedding...")
#         chuck_size = 2000
#         if len(step_text_list) > chuck_size:
#             texts_list = ListUtil.list_of_groups(step_text_list, chuck_size)
#         else:
#             texts_list = [step_text_list]
#         for temp_texts in tqdm(texts_list, ascii=True):
#             print(temp_texts)
#             print("*********************************")
#             response = LLMUtil.client.embeddings.create(input=temp_texts, model=model).data
#             temp_embeddings = []
#             for one_embedding in response:
#                 temp_embeddings.append(one_embedding.embedding)
#             # return embeddings
#             # temp_embeddings = LLMUtil.ask_llm_for_embedding(temp_texts, model)
#             step_embeddings.extend(temp_embeddings)
#
#         index_clusters = util.community_detection(step_embeddings, threshold=STEP_MERGE_THRESHOLD, min_community_size=1)
#
#         for index_cluster in tqdm(index_clusters, ascii=True):
#             cluster = set()
#             for index in index_cluster:
#                 cluster.add(step_text_list[index])
#                 step_index_set.add(index)
#             clusters.append(cluster)
#
#         logging.warning("Merging the rest steps...")
#         for index, step in tqdm(enumerate(step_text_list), ascii=True):
#             if index not in step_index_set:
#                 cluster = set()
#                 cluster.add(step)
#                 clusters.append(cluster)
#
#         index_cluster_dict = dict()
#         for index, cluster in tqdm(enumerate(clusters), ascii=True):
#             index_cluster_dict[index] = index_cluster_dict.get(index, cluster)
#             for step in cluster:
#                 step.cluster_index = index
#
#         self.step_index_cluster_dict = index_cluster_dict


class StepClusterer:
    def __init__(self):
        pass

    @staticmethod
    def cluster_texts_by_fast_clustering(texts, model=LLMUtil.TEXT_EMBEDDING_3_LARGE_MODEL_NAME):
        embeddings = []
        total_cost = 0
        logging.warning("Step embedding...")
        if len(texts) > SYNC_EMBEDDING_NUM:
            texts_list = ListUtil.list_of_groups(texts, SYNC_EMBEDDING_NUM)
        else:
            texts_list = [texts]
        for temp_texts in tqdm(texts_list, ascii=True):
            temp_embeddings, cost = LLMUtil.ask_llm_for_embedding(temp_texts, model)
            embeddings.extend(temp_embeddings)
            total_cost = total_cost + cost

        # Two parameters to tune:
        # min_cluster_size: Only consider cluster that have at least 25 elements
        # threshold: Consider sentence pairs with a cosine-similarity larger than threshold as similar
        # Returns only communities that are larger than min_community_size.
        logging.warning("Step clustering...")
        index_clusters = util.community_detection(embeddings, threshold=STEP_CLUSTER_THRESHOLD,
                                                  min_community_size=1, show_progress_bar=True)
        logging.warning("Post processing...")
        clusters = []
        text_index_set = set()
        for index_cluster in index_clusters:
            cluster = set()
            for index in index_cluster:
                cluster.add(texts[index])
                text_index_set.add(index)
            clusters.append(cluster)

        logging.warning("Merging the rest steps...")
        for index, step in enumerate(texts):
            if index not in text_index_set:
                cluster = set()
                cluster.add(step)
                clusters.append(cluster)
        return clusters, total_cost

    @staticmethod
    def split_steps_by_step_type(step_splitter_output):
        action_steps = []
        check_steps = []
        for one_output in step_splitter_output:
            if one_output:
                answer = one_output[Placeholder.ANSWER]
                if answer:
                    test_scenarios = answer[Placeholder.SCENARIOS]
                    for test_scenario in test_scenarios:
                        for step in test_scenario[Placeholder.STEPS]:
                            if step[Placeholder.STEP_TYPE] == Placeholder.STEP_TYPE_ACTION:
                                action_steps.append(step[Placeholder.STEP])
                            else:
                                check_steps.append(step[Placeholder.STEP])
        return action_steps, check_steps

    @staticmethod
    def get_cluster_index_for_one_step(step, clusters):
        step_text = step[Placeholder.STEP]
        for index, cluster in enumerate(clusters):
            if step_text in cluster:
                step[Placeholder.CLUSTER_INDEX] = step.get(Placeholder.CLUSTER_INDEX, index)
                step[Placeholder.CLUSTER_INDEX] = index
                break
        return step

    @staticmethod
    def get_cluster_index_for_steps(step_splitter_output, action_clusters, check_clusters):
        for one_output in step_splitter_output:
            if one_output:
                answer = one_output[Placeholder.ANSWER]
                if answer:
                    test_scenarios = answer[Placeholder.SCENARIOS]
                    for test_scenario in test_scenarios:
                        for step in test_scenario[Placeholder.STEPS]:
                            # step_text = step[Placeholder.STEP]
                            step_type = step[Placeholder.STEP_TYPE]
                            if step_type == Placeholder.STEP_TYPE_ACTION:
                                StepClusterer.get_cluster_index_for_one_step(step, action_clusters)
                                # print(step)
                            else:
                                StepClusterer.get_cluster_index_for_one_step(step, check_clusters)
                                # print(step)
        return step_splitter_output

    @staticmethod
    def cluster_steps(step_splitter_output):
        action_steps, check_steps = StepClusterer.split_steps_by_step_type(step_splitter_output)
        # print(action_steps)
        # print(check_steps)
        # print(f"All steps: {len(steps)}")
        action_clusters, action_clusters_cost = StepClusterer.cluster_texts_by_fast_clustering(action_steps)
        check_clusters, check_clusters_cost = StepClusterer.cluster_texts_by_fast_clustering(check_steps)
        # print(action_clusters)
        # print(check_clusters)
        step_clusterer_output = StepClusterer.get_cluster_index_for_steps(step_splitter_output,
                                                                          action_clusters, check_clusters)
        cost = action_clusters_cost + check_clusters_cost

        return step_clusterer_output, cost
