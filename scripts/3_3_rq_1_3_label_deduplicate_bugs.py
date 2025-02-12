import json
from pathlib import Path

from tqdm import tqdm

from bug_automating.pipelines.evaluator import Deduplicator, Tagger
from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.llm_util import LLMUtil
from config import DATA_DIR, APP_NAME_WORDPRESS, APP_NAME_FIREFOX, APP_NAME_ANTENNAPOD, OUTPUT_DIR, APP_NAME_AMAZE, \
    APP_NAME_DUCKGO, APP_NAME_MARKOR, APP_NAME_NEWPIPE, APP_NAME_MATERIALFILES

if __name__ == "__main__":
    # app = APP_NAME_FIREFOX
    # app = APP_NAME_ANTENNAPOD
    # app = APP_NAME_WORDPRESS
    # app = APP_NAME_AMAZE
    # app = APP_NAME_DUCKGO
    # app = APP_NAME_MARKOR
    # app = APP_NAME_NEWPIPE
    app = APP_NAME_MATERIALFILES

    filename = f"{app}_deduplicate_bugs"
    save_filename = f"{filename}_with_mark"

    with_kb = True
    # with_kb = False
    with_oracles = True
    # with_oracles = False

    suffix = ''
    if with_kb and not with_oracles:
        suffix = suffix + '_no_oracles'
    elif not with_kb and with_oracles:
        suffix = suffix + '_no_kb'
    filename = filename + suffix
    save_filename = save_filename + suffix

    # all_bugs = Deduplicator.get_all_bugs(app)
    deduplicator_output = FileUtil.load_json(Path(OUTPUT_DIR, f"{filename}.json"))
    try:
        for one_output in deduplicator_output[Placeholder.DEDUPLICATOR_OUTPUT][0:]:
            print(json.dumps(one_output, indent=4))
            # # Get user input for marking
            # user_input = input("Mark this bug as (1) Enhancement or (2) Defect? Enter 1 or 2: ")
            # while True:
            #     if user_input == "1":
            #         one_output[Placeholder.BUG_TYPE] = one_output.get(Placeholder.BUG_TYPE,
            #                                                           Placeholder.TYPE_ENHANCEMENT)
            #         break
            #     elif user_input == "2":
            #         one_output[Placeholder.BUG_TYPE] = one_output.get(Placeholder.BUG_TYPE, Placeholder.TYPE_DEFECT)
            #         break
            #     else:
            #         print("Invalid input. Please enter 1 for Enhancement or 2 for Defect.")
            #         user_input = input()
            tag = Tagger.tag_manually(Tagger.BUG_TYPE_DICT)
            one_output[Placeholder.BUG_TYPE] = one_output.get(Placeholder.BUG_TYPE, tag)

            # tag = Tagger.tag_bug_type_symptom()
            tag = Tagger.tag_manually(Tagger.BUG_TYPE_SYMPTOM_DICT)
            one_output[Placeholder.TYPE_SYMPTOM] = one_output.get(Placeholder.TYPE_SYMPTOM, tag)

            # user_input = input("Mark this bug as (1) Valid or (2) Invalid? Enter 1 or 2: ")
            # while True:
            #     if user_input == "1":
            #         one_output[Placeholder.BUG_VALIDITY] = one_output.get(Placeholder.BUG_VALIDITY,
            #                                                               Placeholder.VALID)
            #         break
            #     elif user_input == "2":
            #         one_output[Placeholder.BUG_VALIDITY] = one_output.get(Placeholder.BUG_VALIDITY,
            #                                                               Placeholder.INVALID)
            #         break
            #     else:
            #         print("Invalid input. Please enter 1 for Valid or 2 for Invalid.")
            #         user_input = input()
            tag = Tagger.tag_manually(Tagger.BUG_VALIDITY_DICT)
            # tag = Tagger.tag_bug_validity()
            one_output[Placeholder.BUG_VALIDITY] = one_output.get(Placeholder.BUG_VALIDITY, tag)

            if one_output[Placeholder.BUG_VALIDITY] == Placeholder.VALID:
                # tag = Tagger.tag_bug_valid_reason()
                tag = Tagger.tag_manually(Tagger.BUG_VALID_REASON_DICT)
                one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON, tag)
                # user_input = input(f"The valid reason: "
                #                    f"\n (1) {Placeholder.VALID_OPTION_1} "
                #                    f"\n (2) {Placeholder.VALID_OPTION_2}: ")
                # while True:
                #     if user_input == "1":
                #         one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
                #                                                                  Placeholder.VALID_OPTION_1)
                #         break
                #     elif user_input == "2":
                #         one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
                #                                                                  Placeholder.VALID_OPTION_2)
                #         break
                #     else:
                #         print("Invalid input. Please re-enter 1 or 2.")
                #         user_input = input()

            if one_output[Placeholder.BUG_VALIDITY] == Placeholder.INVALID:
                # tag = Tagger.tag_bug_invalid_reason()
                tag = Tagger.tag_manually(Tagger.BUG_INVALID_REASON_DICT)
                one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
                                                                         tag)
                # user_input = input(f"The invalid reason: "
                #                    f"\n (1) {Placeholder.INVALID_OPTION_1}"
                #                    f"\n (2) {Placeholder.INVALID_OPTION_2}"
                #                    f"\n (3) {Placeholder.INVALID_OPTION_3}"
                #                    f"\n (4) {Placeholder.INVALID_OPTION_4}"
                #                    f"\n (5) {Placeholder.INVALID_OPTION_5}"
                #                    f"\n (6) {Placeholder.INVALID_OPTION_6}"
                #                    f"\n (7) {Placeholder.INVALID_OPTION_7}"
                #                    f"\n (8) {Placeholder.INVALID_OPTION_8}"
                #                    )
                # while True:
                #     if user_input == "1":
                #         one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
                #                                                                  Placeholder.INVALID_OPTION_1)
                #         break
                #     elif user_input == "2":
                #         one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
                #                                                                  Placeholder.INVALID_OPTION_2)
                #         break
                #     elif user_input == "3":
                #         one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
                #                                                                  Placeholder.INVALID_OPTION_3)
                #         break
                #     elif user_input == "4":
                #         one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
                #                                                                  Placeholder.INVALID_OPTION_4)
                #         break
                #     elif user_input == "5":
                #         one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
                #                                                                  Placeholder.INVALID_OPTION_5)
                #         break
                #     elif user_input == "6":
                #         one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
                #                                                                  Placeholder.INVALID_OPTION_6)
                #         break
                #     elif user_input == "7":
                #         one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
                #                                                                  Placeholder.INVALID_OPTION_7)
                #         break
                #     elif user_input == "8":
                #         one_output[Placeholder.VALIDITY_REASON] = one_output.get(Placeholder.VALIDITY_REASON,
                #                                                                  Placeholder.INVALID_OPTION_8)
                #         break
                #     else:
                #         print("Invalid input. Please re-enter:")
                #         user_input = input()
        FileUtil.dump_json(Path(OUTPUT_DIR, f"{save_filename}.json"), deduplicator_output)
    except Exception as e:
        print(e)
        FileUtil.dump_json(Path(OUTPUT_DIR, f"{save_filename}.json"), deduplicator_output)
        pass
