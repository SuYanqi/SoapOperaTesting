import ast
import copy
import json
from pathlib import Path

from tqdm import tqdm

from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.img_util import ImageUtil
from bug_automating.utils.llm_util import LLMUtil

from config import DATA_DIR, APP_NAME_FIREFOX


class OracleFinder:
    def __init__(self, assistant=None, vector_store=None, thread=None):
        self.assistant = assistant
        self.vector_store = vector_store
        self.thread = thread  # use thread as memory to save conversation

    def initiate_cluster_identifier(self, assistant_id=None, vector_store_id=None, thread_id=None,
                                    app=APP_NAME_FIREFOX, model_name=LLMUtil.GPT4O_MODEL_NAME, temperature=0.2):
        """
        if assistant_id = None, then vector_store_id is None
        """
        if assistant_id is None:
            instructions = (
                f"You are a cluster identifier capable of identifying clusters for the given step.\n"
                f"Each cluster, represented by {Placeholder.CLUSTER_INDEX}, includes steps that involve the same UI operation, "
                f"meaning a consistent set of user interactions that achieve the same result within the user interface.\n"
                f"The given step consists of {Placeholder.STEP}, {Placeholder.ACTION}, {Placeholder.ELEMENT_NAME}, and others. "
                f"{Placeholder.STEP} is the step description. "
                f"{Placeholder.ACTION}, {Placeholder.ELEMENT_NAME}, and others are the specific UI operations, "
                f"i.e., the action executed and its executed UI element.\n"
                f"Based on the given step:\n"
                f"a. Search the file to get the {Placeholder.CLUSTER_INDEX} of steps with the same UI operation as the given step.\n"
                f"b. Return some {Placeholder.REPRESENTATIVE_STEPS} from the {Placeholder.CLUSTER_INDEX} for reference.\n"
                f"Note that the given step can belong to multiple clusters, but only return {Placeholder.CLUSTER_INDEXES} with high confidence.\n"
                f"Double-check the matching between the {Placeholder.CLUSTER_INDEX} and {Placeholder.REPRESENTATIVE_STEPS}.\n"
                f"If no {Placeholder.CLUSTER_INDEXES} are identified, return None."
            )

            vector_store_name = f"{app} Test Scenario Knowledge Base"
            filepath = Path(DATA_DIR, app, "id_scenarios_dicts.json")
            assistant, vector_store = LLMUtil.create_assistant(assistant_name="Cluster Identifier",
                                                               instructions=instructions,
                                                               vector_store_id=vector_store_id,
                                                               vector_store_name=vector_store_name,
                                                               filepath=str(filepath),
                                                               model_name=model_name,
                                                               temperature=temperature)
        else:
            assistant = LLMUtil.retrieve_assistant_by_id(assistant_id)
            vector_store = LLMUtil.retrieve_vector_store_by_id(vector_store_id)

        if thread_id is None:
            thread = LLMUtil.create_thread()
        else:
            thread = LLMUtil.retrieve_thread_by_id(thread_id)

        self.assistant = assistant
        self.vector_store = vector_store
        self.thread = thread
        # return cls(assistant, thread)

    @staticmethod
    def get_text_input_from_operation(operation):
        # oracles = []
        # if with_oracles:
        #     oracles = operation.get(Placeholder.ORACLES, [])
        text_input = {
            Placeholder.STEP: operation.get(Placeholder.STEP, ''),
            Placeholder.ACTION: operation.get(Placeholder.ACTION, ''),
            Placeholder.SCROLL_DIRECTION: operation.get(Placeholder.SCROLL_DIRECTION, ''),
            Placeholder.ELEMENT_NAME: operation.get(Placeholder.ELEMENT_NAME, ''),
            Placeholder.ELEMENT_CATEGORY: operation.get(Placeholder.ELEMENT_CATEGORY, ''),
            # Placeholder.ELEMENT_NUM: operation.get(Placeholder.ELEMENT_NUM, ''),
            Placeholder.ELEMENT_INPUT: operation.get(Placeholder.ELEMENT_INPUT, ''),
            # Placeholder.ORACLES: oracles,
        }
        return text_input

    def question(self, sub_step, with_original_img_filepath=None, with_cots=True):
        operation = ""
        if sub_step:
            operation = self.get_text_input_from_operation(sub_step)
            operation = json.dumps(operation)

        question = f"{operation}\n"

        if with_cots:
            # Create a new dictionary with the new key-value pair first, followed by the original dictionary
            Placeholder.CLUSTER_IDENTIFIER_OUTPUT_FORMAT = {
                Placeholder.CHAIN_OF_THOUGHTS: "The logical reasoning required to identify the clusters for the given step. ",
                **Placeholder.CLUSTER_IDENTIFIER_OUTPUT_FORMAT}

        # f" but only return clusters with high confidence. " \
        json_format_request = f"Please give me the answer in a json format: " \
                              f"{Placeholder.CLUSTER_IDENTIFIER_OUTPUT_FORMAT}"
        text_input = (
                question + "\n" +
                json_format_request
        )
        if with_original_img_filepath:
            text_input = text_input + "\n" + \
                         "The screenshots include the GUI and GUI with coordinate numbers. " \
                         "Please use the GUI for observation and " \
                         "the GUI with coordinate numbers for element location and description."

        return text_input.strip()

    def ask_assistant(self, sub_step=None, with_img_filepath=None, with_original_img_filepath=None,
                      with_instances=True, with_cots=True,
                      app=APP_NAME_FIREFOX, assistant_id=LLMUtil.FENIX_CLUSTER_IDENTIFIER_ASSISTANT_ID,
                      vector_store_id=LLMUtil.FENIX_TEST_SCENARIO_VECTOR_STORE_ID, thread_id=None):
        if self.assistant is None:
            self.initiate_cluster_identifier(assistant_id, vector_store_id, thread_id, app)
        question = self.question(sub_step, with_original_img_filepath, with_cots)
        # print(question)
        thread_messages = LLMUtil.get_thread_messages(self.thread.id, question,
                                                      with_img_filepath, with_original_img_filepath,
                                                      with_instances)
        # print(thread_messages.content)
        run = LLMUtil.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            temperature=0,
        )
        total_cost = LLMUtil.calculate_costs(run)

        messages = list(LLMUtil.client.beta.threads.messages.list(
            thread_id=self.thread.id,
            run_id=run.id))

        LLMUtil.show_thread_messages(self.thread.id)
        # print("*************************************************")
        # print(messages)
        # print("*************************************************")

        message_content = messages[0].content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = LLMUtil.client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.save_filename}")
        finder_output = message_content.value
        return finder_output, total_cost

    def process_ans(self, identifier_output, img_filepath=None):
        # @todo
        executed_step = None
        clusters = None
        # img_filepath = None
        try:
            """
             the input string is not a valid JSON format.
             The string appears to be a Python dictionary representation,
             but it's being treated as a JSON string.
             To fix this issue, Use ast.literal_eval() instead of json.loads():
            """
            identifier_output = ast.literal_eval(identifier_output)
            executed_step = identifier_output.get(Placeholder.EXECUTED_STEP)
            clusters = identifier_output.get(Placeholder.CLUSTERS)
        except Exception as e:
            print(f"Exception: {e}\n{identifier_output}")
            pass

        return executed_step, clusters

    def identify_clusters(self, sub_step=None, with_img_filepath=None, with_original_img_filepath=None,
                          with_instances=True, with_cots=True, with_format_verifier=False
                          #   app='Fenix', assistant_id=None, vector_store_id=None, thread_id=None
                          ):
        identifier_output, identifier_cost = self.ask_assistant(sub_step, with_img_filepath, with_original_img_filepath,
                                                                with_instances, with_cots
                                                                #    app, assistant_id, vector_store_id, thread_id
                                                                )
        if with_format_verifier:
            identifier_output, messages, format_verifier_cost = FormatVerifier.verify_format(identifier_output,
                                                                                             Placeholder.CLUSTER_IDENTIFIER_OUTPUT_FORMAT)
        # total_cost = identifier_cost + format_verifier_cost
        # print(identifier_output)
        # print(type(identifier_output))
        identifier_output = ast.literal_eval(identifier_output)
        identifier_output[Placeholder.ORACLE_FINDER_COST] = identifier_output.get(Placeholder.ORACLE_FINDER_COST,
                                                                                  identifier_cost)
        if with_format_verifier:
            identifier_output[Placeholder.FORMAT_VERIFIER_COST] = identifier_output.get(Placeholder.FORMAT_VERIFIER_COST,
                                                                                        format_verifier_cost)
        identifier_output = json.dumps(identifier_output)
        return json.loads(identifier_output)

    def get_oracles_by_clusters(self, identifier_output, bugs):
        if identifier_output:
            oracles = list()
            clusters = identifier_output[Placeholder.CLUSTERS]
            for cluster in clusters:
                cluster_index = cluster[Placeholder.CLUSTER_INDEX]
                # representative_steps = cluster[Placeholder.REPRESENTATIVE_STEPS]
                # print(f"cluster_index: {cluster_index}")
                steps = []
                if cluster_index:
                    steps = bugs.cluster_index_steps_dict[int(cluster_index)]
                # check_item_indexes = set()
                # temp_steps = set()
                # temp_oracles = []
                for step in steps:
                    # temp_steps.add(step.text)
                    # temp_oracles.extend(step.check_items)
                # if set(representative_steps).intersection(temp_steps):
                    oracles.extend(step.check_items)
            # @todo bugs not do checkitem clustering, so cannot do filtering
        #     this following code aims to filter oracles in the same cluster, only keep one
        #     filtered_oracles = set()
        #     cluster_index_list = []
        #     for check_item in oracles:
        #         if check_item.cluster_index not in cluster_index_list:
        #             cluster_index_list.append(check_item.cluster_index)
        #             filtered_oracles.add(check_item.text)
        #     # print(len(oracles))
        #     # print(len(filtered_oracles))
        #     return list(filtered_oracles)
        # return []
            oracle_list = set()
            for oracle in oracles:
                oracle_list.add(oracle.text)
            return list(oracle_list)
        return[]

    def find_oracles(self, sub_step=None, with_img_filepath=None, with_original_img_filepath=None, bugs=None,
                     with_instances=True, with_cots=True, with_format_verifier=False,
                     #  app=FIREFOX_APP_NAME, assistant_id=None, vector_store_id=None, thread_id=None
                     ):
        identifier_output = self.identify_clusters(sub_step, with_img_filepath, with_original_img_filepath,
                                                   with_instances, with_cots, with_format_verifier
                                                   #    app, assistant_id, vector_store_id, thread_id
                                                   )
        # print(identifier_output)
        oracles = self.get_oracles_by_clusters(identifier_output, bugs)
        # print(f"Oracles: {oracles}")
        # if oracles:
        identifier_output[Placeholder.ORACLES] = identifier_output.get(Placeholder.ORACLES, oracles)
        return identifier_output


class Verifier:
    def __init__(self):
        pass

    @staticmethod
    def convert_instances_into_qa_pairs(bugs):
        # @todo
        qa_pairs = []
        if Placeholder.SCENARIO_MODIFIER_INSTANCES:
            for instance_dict in Placeholder.SCENARIO_MODIFIER_INSTANCES:
                # print(instance_dict['bug_id'])
                bug = bugs.get_bug_by_id(int(instance_dict['bug_id']))
                question = Verifier.question(bug)
                answer = Verifier.answer(instance_dict['output'])
                qa_pairs.append((question, answer))
        return qa_pairs

    @staticmethod
    def get_session_prompt(with_original_gui=True, with_oracles=False, with_cots=True):
        introduction = f"I am a verifier capable of " \
                       f"identifying bugs given the steps and their corresponding GUIs. " \
                       "Please use creative thinking to find any bugs. " \
                       "First, conduct an overall inspection of the GUI to ensure there are no obvious visual issues. " \
                       "Then, separately check each component to ensure its layout is reasonable. " \
                       "Third, check for bugs by analyzing the sequences of images and their corresponding operations. "
        if with_cots:
            # Create a new dictionary with the new key-value pair first, followed by the original dictionary
            Placeholder.VERIFIER_OUTPUT_FORMAT = {
                Placeholder.CHAIN_OF_THOUGHTS: "The logical reasoning required to generate creative thinking oracles and identifying bugs",
                **Placeholder.VERIFIER_OUTPUT_FORMAT}
            # Placeholder.VERIFIER_OUTPUT_FORMAT[Placeholder.CHAIN_OF_THOUGHTS] = \
            #     Placeholder.VERIFIER_OUTPUT_FORMAT.get(Placeholder.CHAIN_OF_THOUGHTS, "")
        json_format_request = f"Please give the answer in a json format: {Placeholder.VERIFIER_OUTPUT_FORMAT}\n"
        notes = [
            f"Note that if no bugs is identified, {Placeholder.BUGS} in the json format is None.",
            "Please return the bugs that are actually observed, do not speculate.",
            f"Note that the GUI is the state after executing the given step. ",
            # "Note that there are oracles for you to identify any bugs, but please do not restrict to these oracles. "
            # "Please use creative thinking to find any bugs based on GUI. ",
        ]
        if with_oracles:
            notes.append("Note that there are oracles for you to identify any bugs, "
                         "but please do not restrict to these oracles. ")
        if with_original_gui:
            notes.append("The screenshot includes the GUI and GUI with coordinate numbers. "
                         "Please use the GUI for observation and "
                         "the GUI with coordinate numbers for element location and description.")
        all_notes = ""
        for note in notes:
            all_notes = all_notes + "\n" + note
        session_prompt = (
                introduction + "\n" +
                # test_scenarios + "\n" +
                # steps + "\n" +
                # actions + "\n" +
                # question + "\n" +
                all_notes + "\n" +
                json_format_request
        )

        return session_prompt

    @staticmethod
    def get_initial_messages(with_original_gui=True, with_instances=None, with_oracles=False, with_cots=True):
        session_prompt = Verifier.get_session_prompt(with_original_gui, with_oracles, with_cots)
        qa_pairs = None
        if with_instances:
            qa_pairs = Verifier.convert_instances_into_qa_pairs(with_instances)
        messages = LLMUtil.get_messages(session_prompt, qa_pairs)
        return messages

    @staticmethod
    def get_text_input_from_operation(operation, oracles=None):
        # if oracles:
        #     oracles = operation.get(Placeholder.ORACLES, oracles)
        text_input = {
            Placeholder.STEP: operation.get(Placeholder.STEP, ''),
            Placeholder.ACTION: operation.get(Placeholder.ACTION, ''),
            Placeholder.SCROLL_DIRECTION: operation.get(Placeholder.SCROLL_DIRECTION, ''),
            Placeholder.ELEMENT_NAME: operation.get(Placeholder.ELEMENT_NAME, ''),
            Placeholder.ELEMENT_CATEGORY: operation.get(Placeholder.ELEMENT_CATEGORY, ''),
            Placeholder.ELEMENT_NUM: operation.get(Placeholder.ELEMENT_NUM, ''),
            Placeholder.ELEMENT_INPUT: operation.get(Placeholder.ELEMENT_INPUT, ''),
            # Placeholder.ORACLES: oracles,
        }
        if oracles:
            text_input[Placeholder.ORACLES] = text_input.get(Placeholder.ORACLES, oracles)
        return text_input

    @staticmethod
    def question(sub_step=None, base64_image_with_nums=None, base64_image=None, oracles=True, img_detail="high"):
        question = []
        text_input = ""
        image_base64_list = [base64_image, base64_image_with_nums]

        for image_base64 in image_base64_list:
            if image_base64:
                image_input = LLMUtil.IMAGE_BASE64_INPUT.format(base64_image=image_base64,
                                                                img_detail=img_detail)
                image_input = json.loads(image_input)
                question.append(image_input)
        if sub_step:
            operation = Verifier.get_text_input_from_operation(sub_step, oracles)
            operation = json.dumps(operation)
            text_input = text_input + operation
            # print(text_input)
            text_input = json.dumps(text_input)
        if text_input:
            text_input = json.dumps(text_input)
            text_input = LLMUtil.TEXT_INPUT.format(text_value=text_input)
            # print(text_input)
            # text_input = json.dumps(text_input)
            text_input = json.loads(text_input)
            # print(text_input)
            question.append(text_input)
        question = json.dumps(question)
        return json.loads(question)

    @staticmethod
    def answer(outputs):
        return json.loads(outputs)

    @staticmethod
    def verify(sub_step=None, base64_image_with_nums=None, base64_image=None,
               # with_original_gui=True,
               oracles=None, with_instances=None, with_cots=True, messages=None,
               model_name=LLMUtil.GPT4O_MODEL_NAME, temperature=1):
        if messages is None:
            messages = Verifier.get_initial_messages(base64_image, with_instances, oracles, with_cots)
        # print(messages)

        # extract summary
        question = Verifier.question(sub_step, base64_image_with_nums, base64_image, oracles)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question, messages)
        # print(self.summary_question)
        # input()
        answer, cost = LLMUtil.ask_llm_for_chat_completions(messages, model_name, temperature)
        answer_dict = Verifier.answer(answer)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_ASSISTANT, answer, messages)

        # LLMUtil.show_messages(messages)
        # question_copy = copy.deepcopy(question)
        # question_copy = LLMUtil.get_question_without_image_encode(question_copy)
        # print(question_copy)
        messages_copy = copy.deepcopy(messages)
        messages_copy = LLMUtil.get_messages_without_image_encode(messages_copy)
        # print(messages_copy)
        LLMUtil.show_messages(messages_copy)
        answer_dict_copy = LLMUtil.add_cost_into_answer(answer_dict, cost)
        # print(answer)
        # messages = LLMUtil.get_messages_without_image_encode(messages)
        return answer_dict_copy, messages


class FormatVerifier:
    def __init__(self):
        pass

    @staticmethod
    def convert_instances_into_qa_pairs(bugs):
        # @todo
        qa_pairs = []
        if Placeholder.SCENARIO_MODIFIER_INSTANCES:
            for instance_dict in Placeholder.SCENARIO_MODIFIER_INSTANCES:
                # print(instance_dict['bug_id'])
                bug = bugs.get_bug_by_id(int(instance_dict['bug_id']))
                question = Verifier.question(bug)
                answer = Verifier.answer(instance_dict['output'])
                qa_pairs.append((question, answer))
        return qa_pairs

    @staticmethod
    def get_session_prompt(format=None):
        introduction = f"I am a format verifier capable of converting input into a specific format. "
        # format = json.loads(format)
        # json_format_request = f"Please convert the input into the format: {format}"

        session_prompt = (
            introduction
            # + "\n" +
            # test_scenarios + "\n" +
            # steps + "\n" +
            # actions + "\n" +
            # question + "\n" +
            # notes + "\n" +
            # json_format_request
        )
        return session_prompt

    @staticmethod
    def get_initial_messages(with_instances=None):
        session_prompt = FormatVerifier.get_session_prompt(with_instances)
        # print(session_prompt)
        qa_pairs = None
        if with_instances:
            qa_pairs = Verifier.convert_instances_into_qa_pairs(with_instances)
        messages = LLMUtil.get_messages(session_prompt, qa_pairs)
        return messages

    @staticmethod
    def question(input, format, with_cots=False):
        question = input
        question = question + f"\nPlease extract the information from the above string and " \
                              f"convert into a JSON format: {format}. "
        if with_cots:
            question = question + "\nPlease do the chain-of-thoughts before answering the question."
        return question

    @staticmethod
    def answer(outputs, chains=None):
        if chains:
            return f"{Placeholder.CHAIN_OF_THOUGHTS}: {chains}\n\n" \
                   f"{Placeholder.OUTPUT}: {outputs}"
        return json.dumps(outputs)

    @staticmethod
    def clear_json_format_values(json_format):
        for key, value in json_format.items():
            if isinstance(value, list):
                json_format[key] = []
            elif isinstance(value, dict):
                json_format[key] = FormatVerifier.clear_json_format_values(value)
            elif isinstance(value, str):
                json_format[key] = ''
            else:
                json_format[key] = None
        return json_format

    @staticmethod
    def verify_format(input_content, json_format, with_instances=False, with_cots=False, model=LLMUtil.GPT4O_MINI_NAME,
                      temperature=0.2):
        json_format = FormatVerifier.clear_json_format_values(json_format)
        # if messages is None:
        messages = FormatVerifier.get_initial_messages(with_instances)
        # LLMUtil.show_messages(messages)
        # extract summary
        question = FormatVerifier.question(input_content, json_format, with_cots)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question, messages)
        # print(self.summary_question)
        # input()
        # print(messages)
        answer, cost = LLMUtil.ask_llm_for_chat_completions(messages, model, temperature)
        # answer = FormatVerifier.answer(answer, with_cots)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_ASSISTANT, answer, messages)

        return answer, messages, cost

