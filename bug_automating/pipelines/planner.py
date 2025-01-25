import ast
import json
import time
from pathlib import Path

from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.pipelines.verifier import FormatVerifier
from bug_automating.utils.llm_util import LLMUtil
from bug_automating.utils.nlp_util import NLPUtil
from config import DATA_DIR, APP_NAME_FIREFOX


class Planner:
    # @todo https://platform.openai.com/docs/guides/function-calling
    # @todo https://cookbook.openai.com/examples/how_to_call_functions_with_chat_models
    def __init__(self, assistant=None, vector_store=None, thread=None):
        self.assistant = assistant
        self.vector_store = vector_store
        self.thread = thread  # use thread as memory to save conversation

    def initiate_planner(self, assistant_id=None, vector_store_id=None, thread_id=None,
                         app=APP_NAME_FIREFOX, model_name=LLMUtil.GPT4O_MODEL_NAME, temperature=0.2):
        if assistant_id is None:
            instructions = "You are a test scenario execution planner. " \
                           "Based on the given test scenario and the current GUI status (the given screenshot), " \
                           "a. observe the current GUI; " \
                           "b. identify the step to be executed; " \
                           "c. search the file to get all relevant test scenarios, which can provide feasible sub-steps for executing the step; " \
                           "d. generate feasible sub-steps to be executed based on the current GUI and relevant test scenarios. "
            vector_store_name = f"{app} Test Scenario Knowledge Base"
            filepath = Path(DATA_DIR, app, "id_scenarios_dicts.json")
            # vector_store_name = f"No Test Scenario Knowledge Base"
            # filepath = Path(DATA_DIR, "id_scenarios_dicts.json")
            assistant, vector_store = LLMUtil.create_assistant(assistant_name="Test Scenario Execution Planner",
                                                               instructions=instructions,
                                                               vector_store_id=vector_store_id,
                                                               vector_store_name=vector_store_name,
                                                               filepath=str(filepath),
                                                               model_name=model_name,
                                                               temperature=temperature
                                                               )
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

    def question(self, steps, with_cots=True):
        steps = f"{Placeholder.STEPS}: {steps}"
        # cots = ""
        if with_cots:
            # cots = f"Please do chain-of-thought reasoning for identifying the step to be executed and " \
            #        f"generating feasible sub-steps to be executed based on the current GUI and relevant test scenarios. "
            # f" (" \
            # f"a. describe the current GUI; " \
            # f"b. identify the step to be executed; " \
            # f"c. search the file to get all relevant test scenarios, which can provide feasible sub-steps for executing the step; " \
            # f"d. generate feasible sub-steps to be executed based on the current GUI and relevant test scenarios.). "
            # Create a new dictionary with the new key-value pair first, followed by the original dictionary
            Placeholder.PLANNER_OUTPUT_FORMAT = {
                Placeholder.CHAIN_OF_THOUGHTS: "The logical reasoning required to identify the step to be executed and generating feasible sub-steps to be executed based on the current GUI and relevant test scenarios.",
                **Placeholder.PLANNER_OUTPUT_FORMAT}

            # Placeholder.PLANNER_OUTPUT_FORMAT[Placeholder.CHAIN_OF_THOUGHTS] = \
            #     Placeholder.PLANNER_OUTPUT_FORMAT.get(Placeholder.CHAIN_OF_THOUGHTS, "")
        json_format_request = f"Please return the feasible steps to be executed in the json format: " \
                              f"{Placeholder.PLANNER_OUTPUT_FORMAT}\n"

        question = (
                steps + "\n" +
                # cots + "\n" +
                json_format_request
        )
        return question

    def ask_assistant(self, steps, with_img_filepath=None, with_cots=True, with_instances=True,
                      app=APP_NAME_FIREFOX, assistant_id=LLMUtil.FENIX_PLANNER_ASSISTANT_ID,
                      vector_store_id=LLMUtil.FENIX_TEST_SCENARIO_VECTOR_STORE_ID, thread_id=None):
        if self.assistant is None:
            self.initiate_planner(assistant_id, vector_store_id, thread_id, app)
        question = self.question(steps, with_cots)
        # print(question)
        thread_messages = LLMUtil.get_thread_messages(self.thread.id, question, with_img_filepath=with_img_filepath,
                                                      with_instances=with_instances)
        # print(thread_messages.content)
        # Create a thread and attach the file to the message

        # self.thread = LLMUtil.client.beta.threads.create(
        #     # thread_id=self.thread.id,
        #     # role="user",
        #     messages=messages
        # )
        # print(f"thread id: {self.thread.id}")
        run = LLMUtil.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )
        total_cost = LLMUtil.calculate_costs(run)

        messages = list(LLMUtil.client.beta.threads.messages.list(
            thread_id=self.thread.id,
            run_id=run.id))

        LLMUtil.show_thread_messages(self.thread.id)
        # print("*****************************************************")
        # print(messages)
        # print("*****************************************************")
        message_content = messages[0].content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = LLMUtil.client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.save_filename}")

        # print(message_content.value)
        # print("\n".join(citations))
        # planner_output = self.add_image_filepath_into_output(with_img_filepath, message_content.value)
        planner_output = message_content.value
        return planner_output, total_cost

    def add_image_filepath_into_output(self, image_filepath, planner_output):
        planner_dict = ast.literal_eval(planner_output)
        planner_dict[Placeholder.PLANNER_OUTPUT][Placeholder.SCREENSHOT] = \
            planner_dict[Placeholder.PLANNER_OUTPUT].get(Placeholder.SCREENSHOT, image_filepath)
        return planner_output

    def process_ans(self, planner_output):
        # current_step = None
        # sub_steps = None
        # all_steps_completion = False
        try:
            """
             the input string is not a valid JSON format. 
             The string appears to be a Python dictionary representation, 
             but it's being treated as a JSON string. 
             To fix this issue, Use ast.literal_eval() instead of json.loads():
            """
            try:
                planner_output = ast.literal_eval(planner_output)
            except Exception as e:
                # @todo
                print(f"Planner.process_ans inner: ast.literal_eval Exception: {e}\n{planner_output}")
                planner_output = json.loads(planner_output)
                pass
            # planner_dict[Placeholder.PLANNER_OUTPUT][Placeholder.SCREENSHOT] = \
            #     planner_dict[Placeholder.PLANNER_OUTPUT].get(Placeholder.SCREENSHOT, image_filepath)
            # planner_result = planner_output.get(Placeholder.PLANNER_OUTPUT)
            # current_step = planner_output.get(Placeholder.CURRENT_STEP)
            # sub_steps = planner_output.get(Placeholder.SUB_STEPS)
            if planner_output[Placeholder.CURRENT_STEP] is None or planner_output[Placeholder.SUB_STEPS] is None:
                all_steps_completion = True
                planner_output[Placeholder.ALL_STEPS_COMPLETION] = all_steps_completion
            # all_steps_completion = planner_output.get(Placeholder.ALL_STEPS_COMPLETION)
            planner_output[Placeholder.ALL_STEPS_COMPLETION] = NLPUtil.convert_str_into_bool\
                (planner_output[Placeholder.ALL_STEPS_COMPLETION])
            # if img_filepath:
            #     self.add_image_filepath_into_output(img_filepath, planner_output)
            #     img_filepath = planner_output.get(Placeholder.SCREENSHOT)
        except Exception as e:
            print(f"Planner.process_ans outter: {e}\n{planner_output}")
            pass

        # return current_step, sub_steps, all_steps_completion
        return planner_output

    def plan(self, steps, with_img_filepath=None, with_cots=True, with_instances=False, with_format_verifier=False
             #  app=FIREFOX_APP_NAME, assistant_id=None, vector_store_id=None, thread_id=None
             ):
        """
        plan
        """
        planner_output, planner_cost = self.ask_assistant(steps, with_img_filepath, with_cots, with_instances,
                                                          # app, assistant_id, vector_store_id, thread_id
                                                          )
        # print(planner_output)
        if with_format_verifier:
            planner_output, _, format_verifier_cost = FormatVerifier.verify_format(planner_output,
                                                                                   Placeholder.PLANNER_OUTPUT_FORMAT)
        # current_step, sub_steps, steps_completion = self.process_ans(planner_output)
        planner_output = self.process_ans(planner_output)

        # steps_completion = False
        # if current_step is None and len(sub_steps) >= 1:
        #     steps_completion = True
        # elif current_step is not None and len(sub_steps) >= 1:
        #     current_step = sub_steps[0]
        # planner_output = ast.literal_eval(planner_output)
        planner_output[Placeholder.PLANNER_COST] = planner_output.get(Placeholder.PLANNER_COST, planner_cost)
        if with_format_verifier:
            planner_output[Placeholder.FORMAT_VERIFIER_COST] = planner_output.get(Placeholder.FORMAT_VERIFIER_COST,
                                                                                  format_verifier_cost)
        planner_output = json.dumps(planner_output)
        # return json.loads(planner_output), current_step, sub_steps, steps_completion
        return json.loads(planner_output)

