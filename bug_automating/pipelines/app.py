import copy
import json
import time
from pathlib import Path

from fpdf import FPDF

from bug_automating.pipelines.finder import Finder
from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.pipelines.planner import Planner
from bug_automating.pipelines.player import ActionExecutor, TestScenarioPlayer, ElementLocator
from bug_automating.pipelines.verifier import Verifier, OracleFinder
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.llm_util import LLMUtil
from config import OUTPUT_DIR, MAX_EXPLORATORY_COUNT, APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, APP_NAME_WORDPRESS


class App:

    def __init__(self):
        pass

    @staticmethod
    def process(
            steps, bugs, app_keyword,
            # planner settings ############
            planner_model=LLMUtil.GPT4O_MODEL_NAME,
            planner_temperature=1,
            with_planner_cots=True,
            with_planner_instances=False,
            with_planner_format_verifier=False,
            with_knowledge_base=True,
            # player settings ############
            player_model=LLMUtil.GPT4O_MODEL_NAME,
            player_temperature=1,
            with_player_cots=True,
            with_player_instances=False,
            with_player_messages=True,
            with_player_history=False,
            with_player_original_gui=False,
            # finder settings ############
            finder_model=LLMUtil.GPT4O_MODEL_NAME,
            finder_temperature=1,
            with_finder_cots=True,
            with_finder_instances=False,
            with_oracles=True,
            with_finder_format_verifier=False,
            # detector settings ############
            verifier_model=LLMUtil.GPT4O_MODEL_NAME,
            verifier_temperature=1,
            with_verifier_cots=True,
            with_verifier_instances=False,
            with_verifier_messages=True,
            with_verifier_original_gui=True,
            # format verifier settings ############
            # format_verifier_model=LLMUtil.GPT4O_MINI_NAME,
            # format_verifier_temperature=0.2,
    ):
        output_list = []
        output_dict = None
        # launch app and return package name
        package_name = ActionExecutor.launch_app(app_keyword)
        time.sleep(6)
        print(package_name)
        sub_dir = 'all'
        if not with_knowledge_base and with_oracles:
            sub_dir = 'ablation_no_kb'
        if package_name:
            filepath = Path(OUTPUT_DIR, app_keyword, sub_dir)
            app_directory, current_time = FileUtil.create_directory_if_not_exists(filepath, package_name)
            output_dict = {
                Placeholder.APP_DIR: app_directory,
                Placeholder.STEPS: steps,
                Placeholder.OUTPUT_LIST: output_list,
            }

            # screenshot_num = 0
            steps_completion = False
            current_step = True  # also as a flag for steps completion, if None, then done
            sub_step = None
            exploratory_count = 0

            if app_keyword == APP_NAME_FIREFOX:
                vector_store_id = LLMUtil.FENIX_TEST_SCENARIO_VECTOR_STORE_ID
                planner_assistant_id = LLMUtil.FENIX_PLANNER_ASSISTANT_ID
                oracle_finder_assistant_id = LLMUtil.FENIX_CLUSTER_IDENTIFIER_ASSISTANT_ID
            elif app_keyword == APP_NAME_ANTENNAPOD:
                vector_store_id = LLMUtil.ANTENNAPOD_TEST_SCENARIO_VECTOR_STORE_ID
                planner_assistant_id = LLMUtil.ANTENNAPOD_PLANNER_ASSISTANT_ID
                oracle_finder_assistant_id = LLMUtil.ANTENNAPOD_CLUSTER_IDENTIFIER_ASSISTANT_ID
            elif app_keyword == APP_NAME_WORDPRESS:
                vector_store_id = LLMUtil.WORDPRESS_TEST_SCENARIO_VECTOR_STORE_ID
                planner_assistant_id = LLMUtil.WORDPRESS_PLANNER_ASSISTANT_ID
                oracle_finder_assistant_id = LLMUtil.WORDPRESS_CLUSTER_IDENTIFIER_ASSISTANT_ID
            planner_vector_store_id = vector_store_id
            oracle_vector_store_id = vector_store_id
            if not with_knowledge_base:
                planner_assistant_id = LLMUtil.NO_KNOWLEDGE_BASE_ASSISTANT_ID
                planner_vector_store_id = LLMUtil.NO_KNOWLEDGE_BASE_VECTOR_STORE_ID

            planner = Planner()
            planner.initiate_planner(assistant_id=planner_assistant_id,
                                     vector_store_id=planner_vector_store_id,
                                     thread_id=None,
                                     app=app_keyword,
                                     model_name=planner_model,
                                     temperature=planner_temperature,
                                     )
            oracle_finder = OracleFinder()
            oracle_finder.initiate_cluster_identifier(assistant_id=oracle_finder_assistant_id,
                                                      vector_store_id=oracle_vector_store_id,
                                                      thread_id=None,
                                                      app=app_keyword,
                                                      model_name=finder_model,
                                                      temperature=finder_temperature,
                                                      )
            verifier_messages = None
            player_messages = None
            try:
                while exploratory_count <= MAX_EXPLORATORY_COUNT:
                    time.sleep(1)
                    screenshot_name = f"{Placeholder.SCREENSHOT}_{exploratory_count}"
                    # screenshot_num = screenshot_num + 1
                    base64_image, base64_image_with_nums, num_coord_dict = ActionExecutor. \
                        capture_and_process_screenshot(app_directory, screenshot_name)
                    screenshot_filepath = str(Path(app_directory, f"{screenshot_name}.png"))
                    # screenshot_with_nums_filepath = str(Path(app_directory,
                    #                                          f"{screenshot_name}{Placeholder.WITH_NUMS}.png"))
                    oracle_finder_output = None
                    # oracles = None
                    if sub_step and with_oracles:
                        print(f"{exploratory_count}^^^OracleFinder^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                        oracle_finder_output = oracle_finder.find_oracles(sub_step=sub_step,
                                                                          with_img_filepath=None,
                                                                          with_original_img_filepath=None,
                                                                          bugs=bugs,
                                                                          with_instances=with_finder_instances,
                                                                          with_cots=with_finder_cots,
                                                                          with_format_verifier=with_finder_format_verifier)
                        oracles = oracle_finder_output[Placeholder.ORACLES]
                        if oracles:
                            with_oracles = oracles
                        print(f"Oracles: {oracles}")
                    print(f"{exploratory_count}^^^Verifier^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                    if with_verifier_original_gui:
                        with_verifier_original_gui = base64_image
                    if not with_verifier_messages:
                        verifier_messages = None
                    verifier_output, verifier_messages = Verifier.verify(sub_step=sub_step,
                                                                         base64_image_with_nums=base64_image_with_nums,
                                                                         base64_image=with_verifier_original_gui,
                                                                         oracles=with_oracles,
                                                                         with_instances=with_verifier_instances,
                                                                         with_cots=with_verifier_cots,
                                                                         messages=verifier_messages,
                                                                         model_name=verifier_model,
                                                                         temperature=verifier_temperature, )
                    output = {
                        Placeholder.SCREENSHOT: str(Path(app_directory, f"{screenshot_name}.png")),
                        Placeholder.SCREENSHOT_WITH_NUMS: str(Path(app_directory,
                                                                   f"{screenshot_name}{Placeholder.WITH_NUMS}.png")),
                        Placeholder.ORACLE_FINDER_OUTPUT: oracle_finder_output,
                        Placeholder.VERIFIER_OUTPUT: verifier_output,
                        Placeholder.PLANNER_OUTPUT: None,
                        Placeholder.PLAYER_OUTPUT: None,
                    }
                    output_list.append(output)
                    if steps_completion or exploratory_count == MAX_EXPLORATORY_COUNT:
                        break
                    # if current_step is None or exploratory_count == MAX_EXPLORATORY_COUNT:
                    #     break
                    # print(verifier_output)
                    print(f"{exploratory_count}^^^Planner^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                    planner_output = planner.plan(steps, screenshot_filepath,
                                                  with_cots=with_planner_cots,
                                                  with_instances=with_planner_instances,
                                                  with_format_verifier=with_planner_format_verifier,
                                                  #   app=app_keyword
                                                  )
                    print(planner_output)
                    steps_completion = planner_output[Placeholder.ALL_STEPS_COMPLETION]
                    current_step = planner_output[Placeholder.CURRENT_STEP]
                    print(f"current_step: {current_step}")
                    print(f"steps_completion: {steps_completion}")
                    print(f"{exploratory_count}^^^Player^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                    player_steps = {
                        Placeholder.CURRENT_STEP: planner_output[Placeholder.CURRENT_STEP],
                        Placeholder.SUB_STEPS: planner_output[Placeholder.SUB_STEPS],
                    }
                    if with_player_original_gui:
                        with_player_original_gui = base64_image
                    history = None
                    if with_player_history:
                        history = copy.deepcopy(player_messages)
                    if not with_player_messages:
                        player_messages = None
                    # if with_player_history:
                    #     with_player_history = player_messages
                    player_output, player_messages = TestScenarioPlayer.play_test_scenario(
                        # current_step,
                        player_steps,
                        base64_image_with_nums,
                        num_coord_dict=num_coord_dict,
                        with_original_gui=with_player_original_gui,
                        history=history,
                        # with_references=True,
                        messages=player_messages,
                        # with_previous_gui=True,
                        with_cots=with_player_cots,
                        with_instances=with_player_instances,
                        model_name=player_model,
                        temperature=player_temperature, )
                    sub_step = player_output
                    output[Placeholder.PLANNER_OUTPUT] = planner_output
                    output[Placeholder.PLAYER_OUTPUT] = player_output
                    exploratory_count = exploratory_count + 1
            except Exception as e:
                print(e)
                pass

            FileUtil.dump_json(Path(app_directory, f"{Placeholder.OUTPUT}.json"), output_dict)
            App.create_pdf(output_dict)
        return output_dict

    @staticmethod
    def create_pdf(output_dict):
        """
        show player output in a pdf
        """
        pdf_filepath = Path(output_dict[Placeholder.APP_DIR], f"{Placeholder.OUTPUT}.pdf")
        output_list = output_dict[Placeholder.OUTPUT_LIST]
        # steps = output_dict[Placeholder.STEPS]
        if output_list:
            pdf = FPDF()
            pdf.add_page()
            steps = output_dict[Placeholder.STEPS]
            text = json.dumps(steps, indent=5)
            # Add text
            pdf.set_font("Arial", size=6)
            line_height = 3  # You can change this value to adjust the line height
            pdf.multi_cell(0, line_height, text)
            for output_dict in output_list:
                pdf.add_page()
                # operation = output_dict[Placeholder.OPERATION]
                # Define the path to the screenshot
                screenshot_path = output_dict[Placeholder.SCREENSHOT_WITH_NUMS]

                # Add the image
                image_width = 50
                pdf.image(str(screenshot_path), x=0, y=2, w=image_width)
                # pdf.add_page()
                # Get current y position to place the image below the text
                # current_y = pdf.get_y()
                # current_x = pdf.get_x()
                text = json.dumps(output_dict, indent=5)
                # Add text
                pdf.set_font("Arial", size=6)
                # Set the position for the text (right beside the image)
                pdf.set_xy(image_width + 2, 2)
                line_height = 3  # You can change this value to adjust the line height

                # Add the text
                pdf.multi_cell(0, line_height, text)
                # pdf.multi_cell(0, current_y + 2, text)
                # except Exception as e:
                #     print(f"When creating a pdf: {e}")
                #     pass

                # Get current y position to place the image below the text
                # current_y = pdf.get_y()

            # Save the temporary PDF
            pdf.output(pdf_filepath)
        return pdf_filepath

    # @staticmethod
    # def process(steps, app_keyword,
    #             with_planner_instances=False,
    #             with_player_instances=False,
    #             with_original_gui=False,
    #             with_player_history=False,
    #             with_player_messages=False,
    #             with_references=False,
    #             with_previous_gui=False,
    #             with_messages=True):
    #     output_list = []
    #     # @todo add planner and verifier output
    #     output_dict = {
    #         Placeholder.APP_DIR: None,
    #         # Placeholder.SCENARIO: scenario,
    #         # Placeholder.SCENARIO: test_scenario,
    #         Placeholder.STEPS: steps,
    #         Placeholder.OUTPUT_LIST: output_list,
    #     }
    #     # launch app and return package name
    #     package_name = ActionExecutor.launch_app(app_keyword)
    #     print(package_name)
    #     if package_name:
    #         app_directory, current_time = FileUtil.create_directory_if_not_exists(OUTPUT_DIR, package_name)
    #
    #         screenshot_num = 0
    #         screenshot_name = f"{Placeholder.SCREENSHOT}_{screenshot_num}"
    #         base64_image, base64_image_with_nums, num_coord_dict = ActionExecutor. \
    #             capture_and_process_screenshot(app_directory, screenshot_name)
    #         # screenshot_filepath = Path(app_directory, f"{screenshot_name}.png")
    #         steps_completion = False
    #         exploratory_count = 0
    #         planner = Planner()
    #         planner.initiate_planner(assistant_id=LLMUtil.FENIX_PLANNER_ASSISTANT_ID)
    #         # player_history = None
    #         # # current_step_no = 0
    #         # # # with_history = False
    #         # messages = None
    #         # start_cluster_index = None
    #         # end_cluster_index = None
    #         # step = steps[0]
    #         # references = None
    #         # while current_step_no < len(steps) - 1 and exploratory_count < MAX_PLAYER_EXPLORATORY_COUNT:
    #         while not steps_completion and exploratory_count < MAX_PLAYER_EXPLORATORY_COUNT:
    #             screenshot_filepath = str(Path(app_directory, f"{screenshot_name}.png"))
    #             # current_step, sub_steps = planner.plan(steps, screenshot_filepath,
    #             #                                        with_instances=with_planner_instances,
    #             #                                        app=app_keyword)
    #             planner_output = planner.ask_assistant(steps, screenshot_filepath,
    #                                                    with_instances=with_planner_instances,
    #                                                    app=app_keyword)
    #             planner_output, _ = FormatVerifier.verify_format(planner_output, Placeholder.PLANNER_OUTPUT_FORMAT)
    #             print(planner_output)
    #             current_step, sub_steps, img_filepath = planner.process_ans(planner_output)
    #             if current_step is None and sub_steps is None:
    #                 steps_completion = True
    #             elif current_step is not None and sub_steps is not None:
    #                 current_step = sub_steps[0]
    #             if with_original_gui:
    #                 with_original_gui = base64_image
    #             # base64_previous_image = None
    #             # base64_previous_image_with_nums = None
    #             # if with_history:
    #             #     player_history, base64_previous_image, base64_previous_image_with_nums = \
    #             #         TestScenarioPlayer.get_player_history(output_dict, with_previous_gui)
    #             #     if not with_original_gui:
    #             #         base64_previous_image = None
    #
    #             # answer, step_identifier_messages = StepIdentifier.identify_step(current_step_no, steps, base64_image)
    #             # current_step_no = current_step_no + 1
    #
    #             # answer, messages = ElementLocator.locate_element(current_step_no, steps,
    #             #                                                  base64_image_with_nums, base64_image,
    #             #                                                  player_history,
    #             #                                                  base64_previous_image_with_nums,
    #             #                                                  base64_previous_image
    #             #                                                  )
    #             # if bugs:
    #             #     if step["id"] == 0:
    #             #         # step = steps[exploratory_count]
    #             #         start_cluster_index = None
    #             #     else:
    #             #         start_cluster_index = end_cluster_index
    #             #     end_cluster_index = step["cluster_index"]
    #             #     reference_paths = TestScenarioPlayer.get_reference_for_missing_steps(start_cluster_index,
    #             #                                                                          end_cluster_index,
    #             #                                                                          bugs)
    #             #     # print(reference_scenarios)
    #             #     print(reference_paths)
    #             #     references = f"These are some relevant paths for reference: {reference_paths}, " \
    #             #                  f"Please show the reference path id that you refer to in the " \
    #             #                  f"{Placeholder.CHAIN_OF_THOUGHTS}"
    #
    #             current_step_completion = False
    #             output = {
    #                 Placeholder.PLANNER_OUTPUT: planner_output,
    #                 Placeholder.PLAYER_VERIFIER_OUTPUT_LIST: []
    #             }
    #             while not current_step_completion:
    #                 player_output, player_messages = TestScenarioPlayer.play_test_scenario(current_step,
    #                                                                                        base64_image_with_nums,
    #                                                                                        num_coord_dict=num_coord_dict,
    #                                                                                        with_original_gui=None,
    #                                                                                        with_history=with_player_history,
    #                                                                                        # with_references=True,
    #                                                                                        with_messages=with_player_messages,
    #                                                                                        # with_previous_gui=True,
    #                                                                                        with_instances=with_player_instances)
    #                 print(type(player_output))
    #                 player_output = TestScenarioPlayer.add_image_filepath_into_output(str(Path(app_directory,
    #                                                                                   f"{screenshot_name}{Placeholder.WITH_NUMS}")),
    #                                                                                   player_output)
    #                 screenshot_num = screenshot_num + 1
    #                 screenshot_name = f"{Placeholder.SCREENSHOT}_{screenshot_num}"
    #                 base64_image, base64_image_with_nums, num_coord_dict = ActionExecutor.capture_and_process_screenshot(
    #                     app_directory,
    #                     screenshot_name)
    #
    #                 # verifier_output = Verifier.verify()
    #                 current_step_completion = True
    #
    #                 player_verifier_output = {
    #                     Placeholder.PLAYER_OUTPUT: player_output,
    #                     # Placeholder.VERIFIER_OUTPUT: verifier_output,
    #                 }
    #                 output[Placeholder.PLAYER_VERIFIER_OUTPUT_LIST].append(player_verifier_output)
    #
    #             # answer, messages = ElementLocator.locate_element(steps,
    #             #                                                  base64_image_with_nums, base64_image,
    #             #                                                  player_history,
    #             #                                                  base64_previous_image_with_nums,
    #             #                                                  base64_previous_image,
    #             #                                                  messages, references=references,
    #             #                                                  )
    #             # print(answer)
    #             # print(type(answer))
    #
    #             # step_no, action, element_coord, element_input, scroll_direction, steps_completion = \
    #             #     ElementLocator.process_ans(
    #             #         answer,
    #             #         num_coord_dict)
    #             # step = steps[step_no]
    #             # # print(f"Element_coord: {element_coord}")
    #             # print(f"******{action} {element_coord} {element_input}******")
    #             # ADBUtil.execute(action, element_coord, answer[Placeholder.ELEMENT_INPUT], scroll_direction)
    #             #
    #             # # messages_without_images = LLMUtil.get_messages_without_image_encode(messages)
    #             # screenshot_operation_dict = {
    #             #     Placeholder.SCREENSHOT: str(Path(app_directory, f"{screenshot_name}.png")),
    #             #     Placeholder.SCREENSHOT_WITH_NUMS: str(
    #             #         Path(app_directory, f"{screenshot_name}{Placeholder.WITH_NUMS}.png")),
    #             #     # "step_identifier": step_identifier_messages,
    #             #     Placeholder.OPERATION: answer,
    #             #     # "messages": messages_without_images,
    #             # }
    #             # screenshot_num = screenshot_num + 1
    #             # screenshot_name = f"{Placeholder.SCREENSHOT}_{screenshot_num}"
    #             # base64_image, base64_image_with_nums, num_coord_dict = ActionExecutor. \
    #             #     capture_and_process_screenshot(app_directory, screenshot_name)
    #             #
    #             # # answer_dict, messages = StepCompleter.complete_step(current_step_no, steps, base64_image_with_nums,
    #             # #                                                     base64_image)
    #             # # print(answer_dict)
    #             # # step_completion, next_step_no = StepCompleter.process_ans(answer_dict)
    #             # # if step_completion:
    #             # #     current_step_no = current_step_no + 1
    #             # #
    #             # # messages_without_images = LLMUtil.get_messages_without_image_encode(messages)
    #             # # screenshot_operation_dict["step_completer"] = screenshot_operation_dict.get("step_completer",
    #             # #                                                                             messages_without_images)
    #             #
    #             # screenshot_operation_list.append(screenshot_operation_dict)
    #             #
    #             # if not with_messages:
    #             #     messages = None
    #             #
    #             # # Configure the logging
    #             # logging.basicConfig(filename=Path(LOG_DIR, f'{package_name}_{current_time}.log'),
    #             #                     level=logging.INFO,
    #             #                     format='%(asctime)s - %(levelname)s - %(message)s')
    #             # logging.info(answer)
    #             # # logging.info(messages)
    #             exploratory_count = exploratory_count + 1
    #             output_list.append(output)
    #             # if don't sleep, out of sync: execute too fast, GUI reaction too slow
    #             # time.sleep(0.5)
    #
    #         # # capture the screenshot of the completed GUI
    #         # screenshot_name = f"{Placeholder.SCREENSHOT}_{screenshot_num}"
    #         # ActionExecutor.capture_and_process_screenshot(
    #         #     app_directory,
    #         #     screenshot_name)
    #         # screenshot_operation_dict = {
    #         #     Placeholder.SCREENSHOT: str(Path(app_directory, f"{screenshot_name}.png")),
    #         #     Placeholder.SCREENSHOT_WITH_NUMS: str(
    #         #         Path(app_directory, f"{screenshot_name}{Placeholder.WITH_NUMS}.png")),
    #         #     Placeholder.OPERATION: None,
    #         # }
    #         # output_list.append(screenshot_operation_dict)
    #         # # messages = LLMUtil.get_messages_without_image_encode(messages)
    #         # output_dict = {
    #         #     Placeholder.APP_DIR: app_directory,
    #         #     "messages": messages,
    #         #     Placeholder.STEPS: steps,
    #         #     Placeholder.SCREENSHOT_OPERATION_LIST: output_list,
    #         # }
    #         # TestScenarioPlayer.create_pdf(output_dict)
    #         FileUtil.dump_json(Path(app_directory, f"{Placeholder.OUTPUT}.json"), output_dict)
    #     return output_dict
