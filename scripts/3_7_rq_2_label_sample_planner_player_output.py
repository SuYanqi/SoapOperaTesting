import json
import os
from pathlib import Path

from tqdm import tqdm

from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from config import DATA_DIR, APP_NAME_WORDPRESS, APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, OUTPUT_DIR

import random


def extract_app_name(file_path):
    """
    Extracts the app name and timestamp part from the given file path.

    Parameters:
    file_path (str): The full file path.

    Returns:
    str: The extracted app name and timestamp.
    """
    # Get the directory name
    directory = os.path.dirname(file_path)

    # Get the base name of the directory (last part of the path)
    return os.path.basename(directory)


if __name__ == "__main__":
    # app = APP_NAME_FIREFOX
    # app = APP_NAME_ANTENNAPOD
    # app = APP_NAME_WORDPRESS
    apps = [APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, APP_NAME_WORDPRESS]
    sample_size = 100
    foldername = 'all'

    save_filename = f"sample_outputs_{foldername}_{sample_size}_with_mark"

    sample_outputs = FileUtil.load_json(Path(OUTPUT_DIR, f'sample_outputs_{foldername}_{sample_size}.json'))
    # sample_play_outputs = FileUtil.load_json(Path(OUTPUT_DIR, f'sample_play_outputs_{foldername}_{sample_size}.json'))

    # for index, one_output in tqdm(enumerate(sample_outputs), ascii=True):
    #     # sample_play_output = sample_play_outputs[index]
    #     print(one_output[Placeholder.SCREENSHOT])
    #     foldername = extract_app_name(one_output[Placeholder.SCREENSHOT])
    #     for app in apps:
    #         if app in foldername:
    #             app_name = app
    #             break
    #
    #     filepath = Path(OUTPUT_DIR, app_name, 'all', foldername, 'OUTPUT.pdf')
    #     FileUtil.open_pdf(filepath)
    #     plan_output = one_output[Placeholder.PLANNER_OUTPUT]
    #     play_output = one_output[Placeholder.PLAYER_OUTPUT]
    # input()

    try:
        for index, one_output in tqdm(enumerate(sample_outputs), ascii=True):
            # sample_play_output = sample_play_outputs[index]
            print(one_output[Placeholder.SCREENSHOT])
            foldername = extract_app_name(one_output[Placeholder.SCREENSHOT])
            for app in apps:
                if app in foldername:
                    app_name = app
                    break

            filepath = Path(OUTPUT_DIR, app_name, 'all', foldername, 'OUTPUT.pdf')
            FileUtil.open_pdf(filepath)
            plan_output = one_output[Placeholder.PLANNER_OUTPUT]
            play_output = one_output[Placeholder.PLAYER_OUTPUT]
            # Print formatted JSON
            formatted_json = json.dumps(plan_output, indent=4)
            print(formatted_json)

            # Get user input for marking
            user_input = input("Mark this current step of plan as (1) Valid or (2) Invalid? Enter 1 or 2: ")
            while True:
                if user_input == "1":
                    one_output[Placeholder.PLAN_CURRENT_STEP_VALIDITY] = \
                        one_output.get(Placeholder.PLAN_CURRENT_STEP_VALIDITY,
                                       Placeholder.VALID)
                    break
                elif user_input == "2":
                    one_output[Placeholder.PLAN_CURRENT_STEP_VALIDITY] = \
                        one_output.get(Placeholder.PLAN_CURRENT_STEP_VALIDITY,
                                       Placeholder.INVALID)
                    break
                else:
                    print("Invalid input. Please enter 1 for Valid or 2 for Invalid.")
                    user_input = input()

            user_input = input("Mark sub-steps of plan by Likert as 1 (worst) - 5 (best). Enter: ")
            while True:
                if user_input == "1" or "2" or "3" or "4" or "5":
                    one_output[Placeholder.PLAN_SUB_STEPS_VALIDITY] = one_output.get(
                        Placeholder.PLAN_SUB_STEPS_VALIDITY,
                        user_input)
                    break
                else:
                    print("Invalid input. Please enter by Likert as 1 (worst) - 5 (best). Enter: ")
                    user_input = input()

            formatted_json = json.dumps(play_output, indent=4)
            print(formatted_json)
            user_input = input("Mark this play step parse of as (1) Valid or (2) Invalid? Enter 1 or 2: ")
            while True:
                if user_input == "1":
                    one_output[Placeholder.PLAY_STEP_PARSE_VALIDITY] = \
                        one_output.get(Placeholder.PLAY_STEP_PARSE_VALIDITY,
                                       Placeholder.VALID)
                    break
                elif user_input == "2":
                    one_output[Placeholder.PLAY_STEP_PARSE_VALIDITY] = one_output.get(
                        Placeholder.PLAY_STEP_PARSE_VALIDITY,
                        Placeholder.INVALID)
                    break
                else:
                    print("Invalid input. Please enter 1 for Valid or 2 for Invalid.")
                    user_input = input()
            if one_output[Placeholder.PLAY_STEP_PARSE_VALIDITY] == Placeholder.INVALID:
                user_input = input(f"The invalid reason: "
                                   f"\n (1) {Placeholder.PLAY_STEP_PARSE_INVALID_OPTION_1}"
                                   f"\n (2) {Placeholder.PLAY_STEP_PARSE_INVALID_OPTION_2}"
                                   f"\n (3) {Placeholder.PLAY_STEP_PARSE_INVALID_OPTION_3}"
                                   # f"\n (4) {Placeholder.INVALID_OPTION_4}"
                                   # f"\n (5) {Placeholder.INVALID_OPTION_5}"
                                   # f"\n (6) {Placeholder.INVALID_OPTION_6}"
                                   # f"\n (7) {Placeholder.INVALID_OPTION_7}"
                                   # f"\n (8) {Placeholder.INVALID_OPTION_8}"
                                   )
                while True:
                    if user_input == "1":
                        one_output[Placeholder.PLAY_STEP_PARSE_INVALIDITY_REASON] = \
                            one_output.get(Placeholder.PLAY_STEP_PARSE_INVALIDITY_REASON,
                                           Placeholder.PLAY_STEP_PARSE_INVALID_OPTION_1)
                        break
                    elif user_input == "2":
                        one_output[Placeholder.PLAY_STEP_PARSE_INVALIDITY_REASON] = \
                            one_output.get(Placeholder.PLAY_STEP_PARSE_INVALIDITY_REASON,
                                           Placeholder.PLAY_STEP_PARSE_INVALID_OPTION_2)
                        break
                    elif user_input == "3":
                        one_output[Placeholder.PLAY_STEP_PARSE_INVALIDITY_REASON] = \
                            one_output.get(Placeholder.PLAY_STEP_PARSE_INVALIDITY_REASON,
                                           Placeholder.PLAY_STEP_PARSE_INVALID_OPTION_3)
                        break
                    else:
                        print("Invalid input. Please re-enter:")
                        user_input = input()

            user_input = input("Mark this play element location as (1) Valid or (2) Invalid? Enter 1 or 2: ")
            while True:
                if user_input == "1":
                    one_output[Placeholder.PLAY_ELEMENT_LOCATION_VALIDITY] = one_output.get(
                        Placeholder.PLAY_ELEMENT_LOCATION_VALIDITY,
                        Placeholder.VALID)
                    break
                elif user_input == "2":
                    one_output[Placeholder.PLAY_ELEMENT_LOCATION_VALIDITY] = one_output.get(
                        Placeholder.PLAY_ELEMENT_LOCATION_VALIDITY,
                        Placeholder.INVALID)
                    break
                else:
                    print("Invalid input. Please enter 1 for Valid or 2 for Invalid.")
                    user_input = input()
            # if one_output[Placeholder.BUG_VALIDITY] == Placeholder.VALID:
            #     user_input = input(f"The valid reason: "
            #                        f"\n (1) {Placeholder.VALID_OPTION_1} "
            #                        f"\n (2) {Placeholder.VALID_OPTION_2}: ")
            #     while True:
            #         if user_input == "1":
            #             one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
            #                                                                      Placeholder.VALID_OPTION_1)
            #             break
            #         elif user_input == "2":
            #             one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
            #                                                                      Placeholder.VALID_OPTION_2)
            #             break
            #         else:
            #             print("Invalid input. Please re-enter 1 or 2.")
            #             user_input = input()
            #
            # if one_output[Placeholder.BUG_VALIDITY] == Placeholder.INVALID:
            #     user_input = input(f"The invalid reason: "
            #                        f"\n (1) {Placeholder.INVALID_OPTION_1}"
            #                        f"\n (2) {Placeholder.INVALID_OPTION_2}"
            #                        f"\n (3) {Placeholder.INVALID_OPTION_3}"
            #                        f"\n (4) {Placeholder.INVALID_OPTION_4}"
            #                        f"\n (5) {Placeholder.INVALID_OPTION_5}"
            #                        f"\n (6) {Placeholder.INVALID_OPTION_6}"
            #                        f"\n (7) {Placeholder.INVALID_OPTION_7}"
            #                        f"\n (8) {Placeholder.INVALID_OPTION_8}"
            #                        )
            #     while True:
            #         if user_input == "1":
            #             one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
            #                                                                      Placeholder.INVALID_OPTION_1)
            #             break
            #         elif user_input == "2":
            #             one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
            #                                                                      Placeholder.INVALID_OPTION_2)
            #             break
            #         elif user_input == "3":
            #             one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
            #                                                                      Placeholder.INVALID_OPTION_3)
            #             break
            #         elif user_input == "4":
            #             one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
            #                                                                      Placeholder.INVALID_OPTION_4)
            #             break
            #         elif user_input == "5":
            #             one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
            #                                                                      Placeholder.INVALID_OPTION_5)
            #             break
            #         elif user_input == "6":
            #             one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
            #                                                                      Placeholder.INVALID_OPTION_6)
            #             break
            #         elif user_input == "7":
            #             one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
            #                                                                      Placeholder.INVALID_OPTION_7)
            #             break
            #         elif user_input == "8":
            #             one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
            #                                                                      Placeholder.INVALID_OPTION_8)
            #             break
            #         else:
            #             print("Invalid input. Please re-enter:")
            #             user_input = input()
            FileUtil.dump_json(Path(OUTPUT_DIR, f"{save_filename}.json"), sample_outputs)
    except Exception as e:
        print(e)
        FileUtil.dump_json(Path(OUTPUT_DIR, f"{save_filename}.json"), sample_outputs)
        pass
