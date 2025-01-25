import ast
import copy
import json
import logging
import re
import time
from collections import defaultdict
from pathlib import Path

from fpdf import FPDF
from tqdm import tqdm

from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.adb_util import ADBUtil
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.img_util import ImageUtil
from bug_automating.utils.llm_util import LLMUtil
from bug_automating.utils.nlp_util import NLPUtil
from config import OUTPUT_DIR, LOG_DIR, MAX_EXPLORATORY_COUNT


class TestScenarioPlayer:
    def __init__(self):
        pass

    @staticmethod
    def get_player_history(messages, with_previous_gui=False):
        step_history_list = []
        # previous_step_history = None

        # steps = output_dict[Placeholder.STEPS]
        # screenshot_operation_list = output_dict[Placeholder.SCREENSHOT_OPERATION_LIST]
        if messages:
            for message in messages:
                if message["role"] == LLMUtil.ROLE_ASSISTANT:
                    message_content = json.loads(message["content"])
                    step = message_content[Placeholder.STEP]
                    action = message_content[Placeholder.ACTION]
                    element_num = message_content[Placeholder.ELEMENT_NUM]
                    element_input = message_content[Placeholder.ELEMENT_INPUT]
                    scroll_direction = message_content[Placeholder.SCROLL_DIRECTION]
                    new_step_history_flag = True

                    for step_history in step_history_list:
                        if step == step_history[Placeholder.STEP]:
                            new_operation_history_flag = True
                            operation_history_list = step_history[Placeholder.OPERATION_HISTORY_LIST]
                            for operation_history in operation_history_list:
                                if action == operation_history[Placeholder.ACTION] and \
                                        element_num == operation_history[Placeholder.ELEMENT_NUM] and \
                                        element_input == operation_history[Placeholder.ELEMENT_INPUT] and \
                                        scroll_direction == operation_history[Placeholder.SCROLL_DIRECTION]:
                                    operation_history[Placeholder.EXECUTION_NUM] = operation_history[
                                                                                       Placeholder.EXECUTION_NUM] + 1
                                    new_operation_history_flag = False
                                    break
                            if new_operation_history_flag:
                                operation_history = {
                                    Placeholder.ACTION: action,
                                    Placeholder.ELEMENT_NUM: element_num,
                                    Placeholder.ELEMENT_INPUT: element_input,
                                    Placeholder.SCROLL_DIRECTION: scroll_direction,
                                    Placeholder.EXECUTION_NUM: 1
                                }
                                operation_history_list.append(operation_history)
                            new_step_history_flag = False
                            # previous_step_history = step_history
                            break
                    if new_step_history_flag:
                        operation_history = {
                            Placeholder.ACTION: action,
                            Placeholder.ELEMENT_NUM: element_num,
                            Placeholder.ELEMENT_INPUT: element_input,
                            Placeholder.SCROLL_DIRECTION: scroll_direction,
                            Placeholder.EXECUTION_NUM: 1
                        }

                        step_history = {
                            # Placeholder.STEP_NO: int(step_num),
                            Placeholder.STEP: step,
                            Placeholder.OPERATION_HISTORY_LIST: [operation_history]
                        }
                        step_history_list.append(step_history)
                        # previous_step_history = step_history

        player_history = {
            Placeholder.STEP_HISTORY_LIST: step_history_list,
            # Placeholder.PREVIOUS_STEP_HISTORY: previous_step_history,
        }
        screenshot_encode = None
        screenshot_with_nums_encode = None
        # if with_previous_gui and screenshot_operation_list:
        #     previous_screenshot_operation = screenshot_operation_list[-1]
        #     screenshot_encode = ImageUtil.encode_image(previous_screenshot_operation[Placeholder.SCREENSHOT])
        #     screenshot_with_nums_encode = ImageUtil.encode_image(
        #         previous_screenshot_operation[Placeholder.SCREENSHOT_WITH_NUMS])

        return json.dumps(player_history), screenshot_encode, screenshot_with_nums_encode

    @staticmethod
    def merge_and_sort_paths_with_frequency(paths):
        """
        input: [
        [{'id': 0, 'text': 'Open the Fenix app with several tabs open.', 'cluster_index': 4038}, {'id': 1, 'text': 'Navigate to Settings.', 'cluster_index': 1}],
        [{'id': 0, 'text': 'Open Firefox for Android.', 'cluster_index': 0}, {'id': 1, 'text': 'Navigate to Settings.', 'cluster_index': 1}],
        [{'id': 0, 'text': 'Go to the three-dot menu.', 'cluster_index': 8}, {'id': 1, 'text': 'Navigate to Settings.', 'cluster_index': 1}],
        [{'id': 0, 'text': 'Access the three-dot menu.', 'cluster_index': 8}, {'id': 1, 'text': 'Navigate to Settings.', 'cluster_index': 1}],
        [{'id': 0, 'text': 'Access the three-dot menu.', 'cluster_index': 8}, {'id': 1, 'text': 'Navigate to Settings.', 'cluster_index': 1}],
        ...
        ]
        output: [
            {
                "id": 0,
                "cluster_indexs": [0, 1],
                "Steps": ["Open Firefox for Android app.", "Navigate to settings."],
                "Frequency": 4
            },
            {
                "id": 1,
                "cluster_indexs": [8, 1],
                "Steps": ["Access the three-dot menu.", "Navigate to Settings."],
                "Frequency": 3
            },
            {
                "id": 2,
                "cluster_indexs": [4038, 1],
                "Steps": ["Open the Fenix app with several tabs open.", "Navigate to Settings."],
                "Frequency": 1
            }
        ]
        """
        # Dictionary to store paths and their frequencies
        path_dict = defaultdict(lambda: {Placeholder.STEPS: [], Placeholder.FREQUENCY: 0})

        # Generate paths and count frequencies
        for path in paths:
            cluster_indexes = tuple(step['cluster_index'] for step in path)
            steps = [step['text'] for step in path]
            path_dict[cluster_indexes][Placeholder.STEPS] = steps
            path_dict[cluster_indexes][Placeholder.FREQUENCY] += 1

        # Convert to the desired output format
        merged_paths = [{"cluster_indexs": list(key), Placeholder.STEPS: value[Placeholder.STEPS],
                         Placeholder.FREQUENCY: value[Placeholder.FREQUENCY]} for
                        key, value in path_dict.items()]
        # Sorting by frequency
        merged_paths = sorted(merged_paths, key=lambda x: x[Placeholder.FREQUENCY], reverse=True)
        # Adding ID to each entry
        merged_paths_with_ids = [{"id": idx, **entry} for idx, entry in enumerate(merged_paths)]

        return merged_paths_with_ids

    @staticmethod
    def get_reference_for_missing_steps(start_index, end_index, bugs):
        """
        1. get all paths
        2. merge and sort paths
        @todo if with start_index and end_index, return [], increase scale by removing start_index?
        """
        paths = bugs.get_paths_with_start_and_end_cluster_index(start_index, end_index)
        paths = TestScenarioPlayer.merge_and_sort_paths_with_frequency(paths)
        return paths

    @staticmethod
    def get_references_for_composite_steps(step, steps=None, assistant_id="asst_uS5qt7cJaBH9CTUsvm0wyErr"):
        # question = f"Please search all steps relevant to '{step}' and return the step and its bug id and summary."
        # question = f"{Placeholder.STEPS}: {steps}\n" \
        #            f"Please search all steps relevant to '{step}' and " \
        #            f"return the steps and their bug ids in the json format: {Placeholder.RETRIEVAL_OUTPUT}."
        question = f"{Placeholder.STEP}: {step}\n" \
                   f"Please search the file to find all possible test scenarios that could detail this step. " \
                   f"Then, return these relevant test scenarios and the referenced bug ids in the json format: " \
                   f"{Placeholder.RETRIEVAL_OUTPUT}. "
        # question = f"{Placeholder.STEP}: {step}\n" \
        #            f"First, search the file to identify whether the given step requires multiple sub-steps to complete. " \
        #            f"If it does, search the file to find all possible test scenarios that could detail this step. " \
        #            f"Finally, based on the current GUI and the relevant test scenarios, " \
        #            f"return the potential detailed steps and the referenced bug ids in the json format: " \
        #            f"{Placeholder.RETRIEVAL_OUTPUT}."
        # print(question)
        # @todo return value process: annotations, json-format
        # @todo this method itself: not return itself
        message_content = LLMUtil.search_with_existing_assistant(question, assistant_id)
        return message_content.value

    @staticmethod
    def get_references(prev_step, current_step, bugs):
        """

        """
        start_cluster_index = None
        if prev_step:
            start_cluster_index = prev_step["cluster_index"]
        end_cluster_index = current_step["cluster_index"]
        reference_paths = TestScenarioPlayer.get_reference_for_missing_steps(start_cluster_index,
                                                                             end_cluster_index,
                                                                             bugs)
        end_cluster_index_steps = bugs.cluster_index_steps_dict[end_cluster_index]
        reference_scenarios = None
        if len(end_cluster_index_steps) < 2:
            reference_scenarios = TestScenarioPlayer.get_references_for_composite_steps(current_step)
        # print(reference_scenarios)
        print(reference_paths)
        # references = f"These are some relevant paths for reference: {reference_paths}, " \
        #              f"Please show the reference path id that you refer to in the " \
        #              f"{Placeholder.CHAIN_OF_THOUGHTS}"
        return reference_paths, reference_scenarios

    @staticmethod
    def play_test_scenario(step, base64_image_with_nums, num_coord_dict,
                           with_original_gui=None, history=None,
                           messages=None,
                           # with_previous_gui=True,
                           with_cots=True,
                           with_instances=False,
                           model_name=LLMUtil.GPT4O_MODEL_NAME,
                           temperature=1.0,
                           ):

        base64_image = None
        if with_original_gui:
            base64_image = with_original_gui
        player_history = None
        if history:
            # print(history)
            player_history, base64_previous_image, base64_previous_image_with_nums = \
                TestScenarioPlayer.get_player_history(messages=history,
                                                      # with_previous_gui
                                                      )
            player_history, _, history_summarizer_cost = HistorySummarizer.summarize_history(player_history,
                                                                                             format=Placeholder.STEP_HISTORY_LIST_FORMAT)
            # print(player_history)

        answer, messages = ElementLocator.locate_element(step,
                                                         base64_image_with_nums, base64_image,
                                                         player_history,
                                                         # base64_previous_image_with_nums,
                                                         # base64_previous_image,
                                                         messages,
                                                         with_cots,
                                                         with_instances,
                                                         model_name,
                                                         temperature
                                                         )

        step, action, element_coord, element_input, scroll_direction = \
            ElementLocator.process_ans(
                answer,
                num_coord_dict)
        #     step = steps[step_no]
        #     # print(f"Element_coord: {element_coord}")
        # print(f"******{action} {element_coord} {element_input}******")
        ADBUtil.execute(action, element_coord, element_input, scroll_direction)
        #
        #     # messages_without_images = LLMUtil.get_messages_without_image_encode(messages)
        #     screenshot_operation_dict = {
        #         Placeholder.SCREENSHOT: str(Path(app_directory, f"{screenshot_name}.png")),
        #         Placeholder.SCREENSHOT_WITH_NUMS: str(
        #             Path(app_directory, f"{screenshot_name}{Placeholder.WITH_NUMS}.png")),
        #         # "step_identifier": step_identifier_messages,
        #         Placeholder.OPERATION: answer,
        #         # "messages": messages_without_images,
        #     }
        return answer, messages

    @staticmethod
    def add_image_filepath_into_output(image_filepath, player_output):
        if type(player_output) is not dict:
            player_output = ast.literal_eval(player_output)
        player_output[Placeholder.SCREENSHOT] = \
            player_output.get(Placeholder.SCREENSHOT, image_filepath)
        return player_output

    @staticmethod
    def create_pdf(output_dict):
        """
        show player output in a pdf
        """
        pdf_filepath = Path(output_dict[Placeholder.APP_DIR], f"{Placeholder.PLAYER_OUTPUT}.pdf")
        screenshot_operation_list = output_dict[Placeholder.SCREENSHOT_OPERATION_LIST]
        steps = output_dict[Placeholder.STEPS]
        if screenshot_operation_list:
            pdf = FPDF()
            # pdf.add_page()
            for screenshot_operation_dict in screenshot_operation_list:
                pdf.add_page()
                operation = screenshot_operation_dict[Placeholder.OPERATION]
                if operation:
                    step_num = operation[Placeholder.STEP_NO]
                    try:
                        step = steps[int(step_num)]
                        text = f'Step: {step}\n' \
                               f'{operation}'
                        # Add text
                        pdf.set_font("Arial", size=12)
                        pdf.multi_cell(0, 10, text)
                    except Exception as e:
                        print(f"When creating a pdf: {e}")
                        pass

                    # Get current y position to place the image below the text
                current_y = pdf.get_y()

                # Define the path to the screenshot
                screenshot_path = screenshot_operation_dict[Placeholder.SCREENSHOT_WITH_NUMS]

                # Add the image
                pdf.image(str(screenshot_path), x=10, y=current_y + 10, w=100)

            # Save the temporary PDF
            pdf.output(pdf_filepath)
        return pdf_filepath

    @staticmethod
    def shift_operations_back(player_output):
        # for player, Given an image and do the element locator
        # but for finder, the operation should correspond to the image after the operation for finding bugs
        # so, shift operations one step back
        new_operation_list = copy.deepcopy(player_output[Placeholder.SCREENSHOT_OPERATION_LIST])
        for i in range(len(new_operation_list) - 1, 0, -1):
            new_operation_list[i][Placeholder.OPERATION] = new_operation_list[i - 1][Placeholder.OPERATION]
        new_operation_list[0][Placeholder.OPERATION] = None

        player_output[Placeholder.SCREENSHOT_OPERATION_LIST] = new_operation_list
        # Output the updated JSON
        # updated_player_output = json.dumps(player_output, indent=4)
        # print(updated_json)
        return player_output

    @staticmethod
    def process_player_output(player_output):
        player_output = TestScenarioPlayer.shift_operations_back(player_output)
        steps = player_output[Placeholder.STEPS]
        operations = player_output[Placeholder.SCREENSHOT_OPERATION_LIST]

        # Initialize a dictionary to hold substeps for each step
        steps_with_substeps = {step[Placeholder.STEP_NO]: {Placeholder.STEP: step[Placeholder.STEP],
                                                           Placeholder.SUB_STEPS: []} for step in steps}

        # last_screenshot = None
        # Assign each operation to its corresponding step
        for operation in operations:
            if operation[Placeholder.OPERATION]:
                step_no = operation[Placeholder.OPERATION][Placeholder.STEP_NO]
                steps_with_substeps[step_no][Placeholder.SUB_STEPS].append(operation)

        # Format the output as a list for better readability
        processed_player_output = [{
            Placeholder.STEP_NO: None,
            Placeholder.STEP: None,
            Placeholder.SUB_STEPS: [player_output[Placeholder.SCREENSHOT_OPERATION_LIST][0]]
        }]
        for step_no in sorted(steps_with_substeps.keys()):
            step = steps_with_substeps[step_no]
            step_entry = {
                Placeholder.STEP_NO: step_no,
                Placeholder.STEP: step[Placeholder.STEP],
                Placeholder.SUB_STEPS: step[Placeholder.SUB_STEPS]
            }
            processed_player_output.append(step_entry)

        return processed_player_output

    @staticmethod
    def add_oracles_to_processed_player_output(test_scenario_dict, processed_player_output):
        for scenario_step in test_scenario_dict['steps']:
            for player_step in processed_player_output:
                if scenario_step['text'] == player_step[Placeholder.STEP]:
                    oracles = scenario_step['check_items']
                    for sub_step in player_step[Placeholder.SUB_STEPS]:
                        if Placeholder.OPERATION in sub_step and sub_step[Placeholder.OPERATION]:
                            sub_step[Placeholder.OPERATION][Placeholder.ORACLES] = [oracle['text'] for oracle in
                                                                                    oracles]
        return processed_player_output


class HistorySummarizer:
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
                question = HistorySummarizer.question(bug)
                answer = HistorySummarizer.answer(instance_dict['output'])
                qa_pairs.append((question, answer))
        return qa_pairs

    @staticmethod
    def get_session_prompt(json_format_request=None):
        introduction = "I am a history summarizer capable of merging similar parts and converting them into a specific format."
        session_prompt = (
            introduction
            # + "\n" +
            # json_format_request
        )
        return session_prompt

    @staticmethod
    def get_initial_messages(with_instances=None, json_format_request=None):
        session_prompt = HistorySummarizer.get_session_prompt(json_format_request)
        # print(session_prompt)
        qa_pairs = None
        if with_instances:
            qa_pairs = HistorySummarizer.convert_instances_into_qa_pairs(with_instances)
        messages = LLMUtil.get_messages(session_prompt, qa_pairs)
        return messages

    @staticmethod
    def question(input, format, with_cots=False):
        question = str(input)
        question = question + f"\nPlease return the answer in a json format: {format}. "
        # question = question + f"\nPlease summarize the information from the above input by merging the similar parts and " \
        #                       f"convert into a JSON format: {format}. "
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
    def summarize_history(input, format=Placeholder.STEP_HISTORY_LIST_FORMAT, with_instances=False,
                          with_cots=False, model=LLMUtil.GPT4O_MINI_NAME,
                          temperature=0.2):
        # @todo, count the number not very accurately
        # if messages is None:
        messages = HistorySummarizer.get_initial_messages(with_instances)
        # LLMUtil.show_messages(messages)
        # extract summary
        question = HistorySummarizer.question(input, format, with_cots)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question, messages)
        # print(self.summary_question)
        # input()
        # print(messages)
        answer, cost = LLMUtil.ask_llm_for_chat_completions(messages, model, temperature)
        # answer = FormatVerifier.answer(answer, with_cots)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_ASSISTANT, answer, messages)

        return answer, messages, cost


class ElementLocator:

    def __init__(self):
        pass

    @staticmethod
    def convert_instances_into_qa_pairs(bugs):
        # @todo
        qa_pairs = []
        if Placeholder.SEC_SPLITTER_INSTANCES:
            for instance_dict in Placeholder.SEC_SPLITTER_INSTANCES:
                bug = bugs.get_bug_by_id(int(instance_dict['bug_id']))
                question = ElementLocator.question(bug)
                answer = ElementLocator.answer(instance_dict['output'])
                qa_pairs.append((question, answer))
        return qa_pairs

    @staticmethod
    def get_session_prompt(with_original_gui=True, with_cots=True):
        # introduction = ("I am a helpful element locator capable of identifying and providing the location of elements "
        #                 "within a GUI, which helps operating on elements in GUI based on specified steps.")
        introduction = (
            "I am a helpful element locator capable of identifying the location of elements within a GUI and the actions "
            "to be executed on them, facilitating operations based on specified steps."
        )
        actions = f"{Placeholder.ACTIONS}: {Placeholder.ACTIONS_INFO}"
        # question = "I want to do the given step, please identify which element I should operate and which action I should use based on the specific GUI. "
        question = "Please identify which element to operate and which action to use based on the given step and specific GUI. "
        notes = [
            f"{Placeholder.HOME} action simulates pressing the home button on the device. ",
            f"{Placeholder.ENTER} action simulates pressing the Enter key on the device. ",
            f"{Placeholder.LANDSCAPE} simulates rotating the device to landscape mode.",
            f"{Placeholder.PORTRAIT} simulates rotating the device to portrait mode.",
            "If scrolling the page results in no change, it means the page cannot be scrolled further or has reached the end. Please try other actions or change the scroll direction. ",
            f"If multiple attempts to operate an element fail (i.e., {Placeholder.EXECUTION_NUM} > 2), please try operating the element using other nearby coordinates. "
        ]
        if with_original_gui:
            notes.append("The screenshot includes the GUI and GUI with coordinate numbers. "
                         "Please use the GUI for observation and the GUI with coordinate numbers for element location.")
        all_notes = ""
        for note in notes:
            all_notes = all_notes + '\n' + note
        if with_cots:
            # Create a new dictionary with the new key-value pair first, followed by the original dictionary
            Placeholder.ELEMENT_LOCATOR_OUTPUT_FORMAT = {
                Placeholder.CHAIN_OF_THOUGHTS: "The logical reasoning required to identify which actions need to be performed, which specific element to perform on this GUI.",
                **Placeholder.ELEMENT_LOCATOR_OUTPUT_FORMAT}
            # Placeholder.ELEMENT_LOCATOR[Placeholder.CHAIN_OF_THOUGHTS] = \
            #     Placeholder.ELEMENT_LOCATOR.get(Placeholder.CHAIN_OF_THOUGHTS,
            #                                     "The logical reasoning required to identify which actions need to be "
            #                                     "performed, which specific element to perform on this GUI.")
        json_format_request = f"Please give me the answer in a json format: {Placeholder.ELEMENT_LOCATOR_OUTPUT_FORMAT}"
        session_prompt = (
                introduction + "\n" +
                actions + "\n" +
                question + "\n" +
                all_notes + "\n" +
                json_format_request
        )
        return session_prompt

    @staticmethod
    def get_initial_messages(with_original_gui=True, with_instances=False, with_cots=True):
        """
        @todo
        """
        session_prompt = ElementLocator.get_session_prompt(with_original_gui, with_cots)
        qa_pairs = None
        if with_instances:
            qa_pairs = ElementLocator.convert_instances_into_qa_pairs(with_instances)
        messages = LLMUtil.get_messages(session_prompt, qa_pairs)
        return messages

    @staticmethod
    def question(text_value, base64_image_with_nums, base64_image=None,
                 # previous_gui_with_nums_encode=None, previous_gui_encode=None,
                 # references=None,
                 img_detail="high"):
        text_value = json.dumps(text_value)
        # print(text_value)
        # print(type(text_value))
        question = []
        text_input = LLMUtil.TEXT_INPUT.format(text_value=text_value)
        # print(text_input)
        text_input = json.loads(text_input)
        # print(type(text_input))
        question.append(text_input)

        image_input_list = [
            # previous_gui_encode, previous_gui_with_nums_encode,
            base64_image, base64_image_with_nums]
        for image_input in image_input_list:
            if image_input:
                image_input = LLMUtil.IMAGE_BASE64_INPUT.format(base64_image=image_input, img_detail=img_detail)
                image_input = json.loads(image_input)
                # print(type(image_input))
                question.append(image_input)
        question = json.dumps(question)
        return json.loads(question)

    @staticmethod
    def question_with_2_images(text_value, base64_image, base64_image1, img_detail="high"):
        question = LLMUtil.QUESTION_WITH_2_IMAGE_BASE64.format(
            text_value=text_value,
            base64_image=base64_image,
            base64_image1=base64_image1,
            img_detail=img_detail
        )
        return json.loads(question)

    @staticmethod
    def answer(outputs):
        return json.loads(outputs)

    @staticmethod
    def locate_element(step, base64_image_with_nums, base64_image=None,
                       player_history=None,
                       # base64_previous_image_with_nums=None, base64_previous_image=None,
                       messages=None,
                       # with_instances=False, references=None,
                       with_cots=True,
                       with_instances=False,
                       model_name=LLMUtil.GPT4O_MODEL_NAME,
                       temperature=1.0,
                       img_detail="high",
                       ):
        if messages is None:
            messages = ElementLocator.get_initial_messages(base64_image, with_instances, with_cots)

        text_value = f"{step}\n"

        if player_history:
            # player_history = TestScenarioPlayer.get_player_history(with_history)
            text_value = text_value + 'Below are the steps that have been executed and the operations attempted to perform the corresponding steps: \n' \
                                      f'{player_history}. \n' \
                                      f'Please summarize the wrong attempts based on {Placeholder.STEP_HISTORY_LIST} and ' \
                                      f'avoid repeating ineffective operations. \n'

        question = ElementLocator.question(text_value, base64_image_with_nums, base64_image,
                                           # base64_previous_image_with_nums, base64_previous_image,
                                           # references,
                                           img_detail)
        # question_copy = copy.deepcopy(question)
        # question_copy = LLMUtil.get_question_without_image_encode(question_copy)
        # print(question_copy)

        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question, messages)
        # messages_copy = copy.deepcopy(messages)
        # messages_copy = LLMUtil.get_messages_without_image_encode(messages_copy)
        # print(messages_copy)
        answer, cost = LLMUtil.ask_llm_for_chat_completions(messages, model_name, temperature)
        answer_dict = ElementLocator.answer(answer)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_ASSISTANT, answer, messages)
        messages_copy = copy.deepcopy(messages)
        messages_copy = LLMUtil.get_messages_without_image_encode(messages_copy)
        LLMUtil.show_messages(messages_copy)
        # question_without_image_encode = LLMUtil.get_question_without_image_encode(question)
        # print(question_without_image_encode)
        answer_dict_copy = LLMUtil.add_cost_into_answer(answer_dict, cost)
        return answer_dict_copy, messages

    @staticmethod
    def process_element_num(element_num):
        if isinstance(element_num, int):
            return element_num
        elif isinstance(element_num, str):
            # Extract all numbers from the string
            numbers = list(map(int, re.findall(r'\d+', element_num)))
            if len(numbers) > 0:
                # Calculate the middle number
                middle_index = len(numbers) // 2
                return numbers[middle_index]
            # If no numbers are found or element_num is neither int nor a string with numbers
        return None

    @staticmethod
    def process_ans(answer_dict, num_coord_dict):
        player_output = answer_dict
        step = player_output.get(Placeholder.STEP)
        action = player_output.get(Placeholder.ACTION)
        element_num = player_output.get(Placeholder.ELEMENT_NUM)
        element_num = ElementLocator.process_element_num(element_num)
        element_coord = None
        element_input = player_output.get(Placeholder.ELEMENT_INPUT)
        scroll_direction = player_output.get(Placeholder.SCROLL_DIRECTION)
        # scroll_direction = None
        # steps_completion = False
        # if action != Placeholder.SCROLL and element_num and element_num != "None":
        if element_num and element_num != "None":
            element_coord = num_coord_dict.get(int(element_num))
            element_input = player_output.get(Placeholder.ELEMENT_INPUT)
        # if action == Placeholder.SCROLL:
        # scroll_direction = player_output.get(Placeholder.SCROLL_DIRECTION)

        # steps_completion = answer_dict.get(Placeholder.ALL_STEPS_COMPLETION)
        # steps_completion = NLPUtil.convert_str_into_bool(steps_completion)
        #
        # composite_step = answer_dict.get(Placeholder.COMPOSITE_STEP)
        # # composite_step = NLPUtil.convert_str_into_bool(composite_step)

        # if type(steps_completion) is not bool:
        #     if steps_completion.lower() == 'true':
        #         steps_completion = True
        #     elif steps_completion.lower() == 'false':
        #         steps_completion = False
        #     else:
        #         raise ValueError(f"Invalid literal for boolean: '{steps_completion}'")
        return step, action, element_coord, element_input, scroll_direction
        # , steps_completion

        # return action, element_coord, element_input, scroll_direction, steps_completion

    @staticmethod
    def get_messages_list_for_bugs(bugs, with_instances=False):
        # @todo
        initial_messages = ElementLocator.get_initial_messages(with_instances)
        # print(initial_messages)
        messages_list = []
        for bug in tqdm(bugs, ascii=True):
            question = ElementLocator.question(bug)
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

    # @staticmethod
    # def get_element_coordinate(element_num, num_coord_dict):
    #     return num_coord_dict[element_num]


class ActionExecutor:
    @staticmethod
    def launch_app(app_keyword):
        """
        close the app
        launch the app
        """
        package_name = None
        if not ADBUtil.check_adb_connection():
            print("No devices/emulators found or device is unauthorized. "
                  "Please connect a device, start an emulator, or authorize the device.")
        # Find packages by keyword
        matching_packages = ADBUtil.find_package_by_keyword(app_keyword)
        print(f"\nPackages matching '{app_keyword}':\n", matching_packages)
        if matching_packages:
            # Launch the app
            package_name = matching_packages[0]
            # app_directory, current_time = FileUtil.create_directory_if_not_exists(OUTPUT_DIR, package_name)
            activity_name = ADBUtil.get_main_activity(package_name)  # Replace with the correct activity name
            # ADBUtil.close_app(package_name)
            ADBUtil.launch_app(package_name, activity_name)
        return package_name

    @staticmethod
    def capture_and_process_screenshot(app_directory, screenshot_name):
        """
        capture the current screenshot of GUI
        set the screenshot with nums
        return base64_image_with_nums (screenshot with nums),
               num_coord_dict
        """
        # time.sleep(0.5)
        screenshot_filepath = Path(app_directory, f"{screenshot_name}.png")
        ADBUtil.capture_screenshot(str(screenshot_filepath))
        # ADBUtil.capture_screenshot_by_take_screenshot_button(str(screenshot_filepath))
        # print(f"Screenshot saved to {screenshot_directory}.")
        image, num_coord_dict = ImageUtil.set_img_with_nums(app_directory, screenshot_name)
        image_name_with_nums = f"{screenshot_name}{Placeholder.WITH_NUMS}"
        screenshot_with_nums_filepath = Path(app_directory, f"{image_name_with_nums}.png")
        base64_image = ImageUtil.encode_image(screenshot_filepath)
        base64_image_with_nums = ImageUtil.encode_image(screenshot_with_nums_filepath)
        return base64_image, base64_image_with_nums, num_coord_dict


class StepIdentifier:
    def __init__(self):
        pass

    @staticmethod
    def convert_instances_into_qa_pairs(bugs):
        # @todo
        qa_pairs = []
        if Placeholder.SEC_SPLITTER_INSTANCES:
            for instance_dict in Placeholder.SEC_SPLITTER_INSTANCES:
                bug = bugs.get_bug_by_id(int(instance_dict['bug_id']))
                question = ElementLocator.question(bug)
                answer = ElementLocator.answer(instance_dict['output'])
                qa_pairs.append((question, answer))
        return qa_pairs

    @staticmethod
    def get_session_prompt(steps):
        introduction = ("I am a useful step identifier that can "
                        "determine based on the current GUI and the steps to be completed: "
                        "Whether there are any missing steps to achieve the target step, and "
                        "provide the missing steps; "
                        "Identify whether the step is a compound step, "
                        "whether multiple sub-steps are needed to complete it, and provide the sub-steps.")
        steps = f"{Placeholder.STEPS}: {steps}"
        # question = ""
        # notes = f'Note that if scrolling the page results in no change, ' \
        #         f'it means that the page cannot be scrolled further or has reached the end. ' \
        #         f'Please try other actions or change the scroll direction. \n' \
        #         f'Note that if multiple attempts to operate an element fail (i.e., {Placeholder.EXECUTION_NUM} > 2), ' \
        #         f'please try operating the element by using other coordinate numbers close to it.'
        # "Note that some steps require multiple operations to complete.\n" \
        json_format_request = f"Please give me the answer in a json format: {Placeholder.STEP_IDENTIFIER}"

        session_prompt = (
                introduction + "\n" +
                steps + "\n" +
                # actions + "\n" +
                # question + "\n" +
                # notes + "\n" +
                json_format_request
        )

        return session_prompt

    @staticmethod
    def get_initial_messages(steps, with_instances=False):
        """
        @todo
        """
        session_prompt = StepIdentifier.get_session_prompt(steps)
        qa_pairs = None
        if with_instances:
            qa_pairs = StepIdentifier.convert_instances_into_qa_pairs(with_instances)
        messages = LLMUtil.get_messages(session_prompt, qa_pairs)
        return messages

    @staticmethod
    def question(text_value, base64_image=None,
                 # previous_gui_with_nums_encode=None, previous_gui_encode=None,
                 img_detail="high"):
        # print(text_value)
        text_value = json.dumps(text_value)
        # print(text_value)
        # print(type(text_value))
        question = []
        text_input = LLMUtil.TEXT_INPUT.format(text_value=text_value)
        # print(text_input)
        text_input = json.loads(text_input)
        # print(type(text_input))
        question.append(text_input)
        image_input_list = [base64_image]
        for image_input in image_input_list:
            if image_input:
                image_input = LLMUtil.IMAGE_BASE64_INPUT.format(base64_image=image_input, img_detail=img_detail)
                image_input = json.loads(image_input)
                # print(type(image_input))
                question.append(image_input)
        question = json.dumps(question)
        return json.loads(question)

    @staticmethod
    def answer(outputs):
        return json.loads(outputs)

    @staticmethod
    def identify_step(step_no, steps, base64_image=None,
                      with_instances=False, img_detail="high"):
        # if messages is None:
        messages = StepIdentifier.get_initial_messages(steps, with_instances)
        print(messages)
        # image_number = 1
        text_value = f"Target step: {steps[step_no]}. " \
                     f"Based on the current GUI, determine whether the step is a compound step, " \
                     f"whether multiple sub-steps are needed to complete the step; " \
                     f"determine whether the target element to be executed in the step is on the current page. " \
                     f"If it is present and can be executed directly, there are no missing steps; " \
                     f"otherwise, there are missing steps."
        # if base64_image:
        #     text_value = text_value + "Please use the GUI for observation and the GUI with coordinate numbers for element location. \n"
        #
        # if player_history:
        #     # player_history = TestScenarioPlayer.get_player_history(with_history)
        #     text_value = text_value + 'Below are the steps that have been executed and the operations attempted to perform the corresponding steps: \n' \
        #                               f'{player_history}. \n' \
        #                               f'First, based on the current GUI, determine whether {Placeholder.OPERATION} in {Placeholder.PREVIOUS_STEP_HISTORY} has completed the corresponding {Placeholder.STEP}. ' \
        #                               f'If it has been completed, proceed to the next step. ' \
        #                               f'If it has not been completed, attempt other operations to complete the corresponding step. \n' \
        #                               f'Note that refer to {Placeholder.STEP_HISTORY_LIST} to avoid repeating ineffective operations. \n' \
        #                               f'Note that if multiple attempts to operate an element fail (i.e., {Placeholder.EXECUTION_NUM} > 2), ' \
        #                               f'please summarize the wrong attempts based on {Placeholder.STEP_HISTORY_LIST} and ' \
        #                               f'try to operate the element by using other possible coordinate numbers.'
        # else:
        #     text_value = text_value + "Please identify which element I should operate and " \
        #                               "which action I should use based on the current GUI. "

        question = StepIdentifier.question(text_value, base64_image,
                                           # base64_previous_image_with_nums, base64_previous_image,
                                           img_detail)
        # print(question)

        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question, messages)
        # messages = json.dumps(messages)
        # LLMUtil.show_messages(messages)
        # # LLMUtil.calculate_tokens(messages)
        answer = LLMUtil.ask_llm_for_chat_completions(messages)
        answer_dict = StepIdentifier.answer(answer)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_ASSISTANT, answer, messages)
        question_without_image_encode = LLMUtil.get_question_without_image_encode(question)
        messages = LLMUtil.get_messages_without_image_encode(messages)
        print(question_without_image_encode)
        print(answer)
        return answer_dict, messages

    @staticmethod
    def process_ans(answer_dict, num_coord_dict):
        action = answer_dict.get(Placeholder.ACTION)
        element_num = answer_dict.get(Placeholder.ELEMENT_NUM)
        element_coord = None
        element_input = None
        scroll_direction = None
        if element_num and element_num != "None":
            element_coord = num_coord_dict.get(int(element_num))
            element_input = answer_dict.get(Placeholder.ELEMENT_INPUT)
        if action == Placeholder.SCROLL:
            scroll_direction = answer_dict.get(Placeholder.SCROLL_DIRECTION)

        missing_step = answer_dict.get(Placeholder.MISSING_STEP)
        # missing_step = NLPUtil.convert_str_into_bool(missing_step)

        composite_step = answer_dict.get(Placeholder.COMPOSITE_STEP)
        # composite_step = NLPUtil.convert_str_into_bool(composite_step)

        # if type(steps_completion) is not bool:
        #     if steps_completion.lower() == 'true':
        #         steps_completion = True
        #     elif steps_completion.lower() == 'false':
        #         steps_completion = False
        #     else:
        #         raise ValueError(f"Invalid literal for boolean: '{steps_completion}'")
        return action, element_coord, element_input, scroll_direction, missing_step, composite_step

        # return action, element_coord, element_input, scroll_direction, steps_completion


class StepCompleter:

    def __init__(self):
        pass

    @staticmethod
    def convert_instances_into_qa_pairs(bugs):
        # @todo
        qa_pairs = []
        if Placeholder.SEC_SPLITTER_INSTANCES:
            for instance_dict in Placeholder.SEC_SPLITTER_INSTANCES:
                bug = bugs.get_bug_by_id(int(instance_dict['bug_id']))
                question = ElementLocator.question(bug)
                answer = ElementLocator.answer(instance_dict['output'])
                qa_pairs.append((question, answer))
        return qa_pairs

    @staticmethod
    def get_session_prompt(steps=None):
        introduction = (
            "I am a helpful step completer capable of identifying if the step is completed by the given GUI, "
            # "which helps operating on elements in GUI based on specified steps."
        )
        # Convert the steps into the desired format
        steps = [{f"{Placeholder.CURRENT_STEP_NUM}": i + 1, f"{Placeholder.STEP}": step} for i, step in
                 enumerate(steps)]
        # steps = f"{Placeholder.STEPS}: {steps}"
        # question = "I want to do these steps, please identify which element I should operate and which action I should use based on the specific GUI. "
        # actions = f"{Placeholder.ACTIONS}: {Placeholder.ACTIONS_INFO}"
        # notes = "Note that some steps require multiple operations to complete.\n" \
        #         f'Note that if scrolling the page results in no change, ' \
        #         f'it means that the page cannot be scrolled further or has reached the end. ' \
        #         f'Please try other actions or change the scroll direction. \n' \
        #         f'Note that if multiple attempts to operate an element fail (i.e., {Placeholder.EXECUTION_NUM} > 2), ' \
        #         f'please try operating the element by using other coordinate numbers close to it.'
        json_format_request = f"Please give me the answer in a json format: {Placeholder.STEP_COMPLETER}"

        session_prompt = (
                introduction + "\n" +
                # steps + "\n" +
                # actions + "\n" +
                # question + "\n" +
                # notes + "\n" +
                json_format_request
        )

        return session_prompt

    @staticmethod
    def get_initial_messages(steps, with_instances=False):
        """
        @todo
        """
        session_prompt = StepCompleter.get_session_prompt(steps)
        qa_pairs = None
        if with_instances:
            qa_pairs = StepCompleter.convert_instances_into_qa_pairs(with_instances)
        messages = LLMUtil.get_messages(session_prompt, qa_pairs)
        return messages

    @staticmethod
    def question(text_value, base64_image_with_nums, base64_image=None,
                 img_detail="high"):
        # print(text_value)
        text_value = json.dumps(text_value)
        # print(text_value)
        # print(type(text_value))
        question = []
        text_input = LLMUtil.TEXT_INPUT.format(text_value=text_value)
        # print(text_input)
        text_input = json.loads(text_input)
        # print(type(text_input))
        question.append(text_input)
        image_input_list = [base64_image, base64_image_with_nums]
        for image_input in image_input_list:
            if image_input:
                image_input = LLMUtil.IMAGE_BASE64_INPUT.format(base64_image=image_input, img_detail=img_detail)
                image_input = json.loads(image_input)
                # print(type(image_input))
                question.append(image_input)
        question = json.dumps(question)
        return json.loads(question)

    @staticmethod
    def answer(outputs):
        return json.loads(outputs)

    # @staticmethod
    # def locate_element(steps, base64_image_with_nums, base64_image=None,
    #                    player_history=None, base64_previous_image_with_nums=None, base64_previous_image=None,
    #                    with_instances=False, img_detail="high"):
    #     # if messages is None:
    #     messages = ElementLocator.get_initial_messages(steps, with_instances)
    #     print(messages)
    #     image_number = 1
    #     text_value = ""
    #     if player_history and base64_previous_image:
    #         text_value = text_value + f"No. {image_number} GUI is the previous GUI. \n"
    #         image_number = image_number + 1
    #     if player_history and base64_previous_image_with_nums:
    #         text_value = text_value + f"No. {image_number} GUI is the previous GUI with coordinate numbers. \n"
    #         image_number = image_number + 1
    #     if base64_image:
    #         text_value = text_value + f"No. {image_number} GUI is the current GUI. \n"
    #         image_number = image_number + 1
    #     if base64_image_with_nums:
    #         text_value = text_value + f"No. {image_number} GUI is the current GUI with coordinate numbers. \n"
    #         # image_number = image_number + 1
    #     # LLMUtil.show_messages(messages)
    #     if base64_image:
    #         text_value = text_value + "Please use the GUI for observation and the GUI with coordinate numbers for element location. \n"
    #
    #     if player_history:
    #         # player_history = TestScenarioPlayer.get_player_history(with_history)
    #         text_value = text_value + 'Below are the steps that have been executed and the operations attempted to perform the corresponding steps: \n' \
    #                                   f'{player_history}. \n' \
    #                                   f'First, based on the current GUI, determine whether {Placeholder.OPERATION} in {Placeholder.PREVIOUS_STEP_HISTORY} has completed the corresponding {Placeholder.STEP}. ' \
    #                                   f'If it has been completed, proceed to the next step. ' \
    #                                   f'If it has not been completed, attempt other operations to complete the corresponding step. \n' \
    #                                   f'Note that refer to {Placeholder.STEP_HISTORY_LIST} to avoid repeating ineffective operations. \n' \
    #                                   f'Note that if multiple attempts to operate an element fail (i.e., {Placeholder.EXECUTION_NUM} > 2), ' \
    #                                   f'please summarize the wrong attempts based on {Placeholder.STEP_HISTORY_LIST} and ' \
    #                                   f'try to operate the element by using other possible coordinate numbers.'
    #     else:
    #         text_value = text_value + "Please identify which element I should operate and " \
    #                                   "which action I should use based on the current GUI. "
    #
    #     question = ElementLocator.question(text_value, base64_image_with_nums, base64_image,
    #                                        base64_previous_image_with_nums, base64_previous_image,
    #                                        img_detail)
    #     # print(question)
    #
    #     messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question, messages)
    #     # messages = json.dumps(messages)
    #     # LLMUtil.show_messages(messages)
    #     # # LLMUtil.calculate_tokens(messages)
    #     answer = LLMUtil.ask_llm_for_chat_completions(messages)
    #     answer_dict = ElementLocator.answer(answer)
    #     messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_ASSISTANT, answer, messages)
    #     question_without_image_encode = LLMUtil.get_question_without_image_encode(question)
    #     print(question_without_image_encode)
    #     return answer_dict, messages

    @staticmethod
    def complete_step(current_step_no, steps, base64_image_with_nums, base64_image=None,
                      with_instances=False, img_detail="high"):
        # if messages is None:
        messages = StepCompleter.get_initial_messages(steps, with_instances)
        print(messages)
        image_number = 1
        text_value = f"{Placeholder.STEP}: {steps[current_step_no]}\n"
        if base64_image:
            text_value = text_value + f"No. {image_number} GUI is the current GUI. \n"
            image_number = image_number + 1
        if base64_image_with_nums:
            text_value = text_value + f"No. {image_number} GUI is the current GUI with coordinate numbers. \n"
            # image_number = image_number + 1
        # LLMUtil.show_messages(messages)
        if base64_image:
            text_value = text_value + "Please use the GUI for observation and the GUI with coordinate numbers for element location. \n"

        question = StepCompleter.question(text_value, base64_image_with_nums, base64_image,
                                          img_detail)
        # print(question)

        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question, messages)
        # messages = json.dumps(messages)
        # LLMUtil.show_messages(messages)
        # # LLMUtil.calculate_tokens(messages)
        answer = LLMUtil.ask_llm_for_chat_completions(messages)
        answer_dict = StepCompleter.answer(answer)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_ASSISTANT, answer, messages)
        question_without_image_encode = LLMUtil.get_question_without_image_encode(question)
        print(question_without_image_encode)
        return answer_dict, messages

    @staticmethod
    def process_ans(answer_dict):

        step_completion = answer_dict.get(Placeholder.STEP_COMPLETION)
        if type(step_completion) is not bool:
            if step_completion.lower() == 'true':
                step_completion = True
            elif step_completion.lower() == 'false':
                step_completion = False
            else:
                raise ValueError(f"Invalid literal for boolean: '{step_completion}'")
        next_step_no = answer_dict.get(Placeholder.NEXT_STEP_NO)

        return step_completion, next_step_no
