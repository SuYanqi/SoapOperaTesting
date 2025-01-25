import json
from collections import defaultdict
from pathlib import Path

from tqdm import tqdm

from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.list_util import ListUtil
from bug_automating.utils.llm_util import LLMUtil

from config import OUTPUT_DIR


class Deduplicator:
    def __init__(self):
        pass

    @staticmethod
    def convert_instances_into_qa_pairs(bugs):
        # @todo
        qa_pairs = []
        if Placeholder.SCENARIO_MODIFIER_INSTANCES:
            for instance_dict in Placeholder.SCENARIO_MODIFIER_INSTANCES:
                pass
                # # print(instance_dict['bug_id'])
                # bug = bugs.get_bug_by_id(int(instance_dict['bug_id']))
                # question = Verifier.question(bug)
                # answer = Verifier.answer(instance_dict['output'])
                # qa_pairs.append((question, answer))
        return qa_pairs

    @staticmethod
    def get_session_prompt(with_instances=None, format=Placeholder.DEDUPLICATOR_FORMAT):
        # Basic introduction message for the bug deduplicator
        introduction = (
            "I am a bug deduplicator designed to identify and merge duplicate bugs. "
            "The output will maintain the same number of bugs as the input, "
            "ensuring that each issue, including those without duplicates, "
            f"is fully represented with all its fields "
            f"(e.g., {Placeholder.SUMMARY}, {Placeholder.STEPS_TO_REPRODUCE}, {Placeholder.EXPECTED_BEHAVIORS})."
        )

        # If a specific format is provided, include a conversion request in the prompt
        json_format_request = f"Please answer in the json format: {format}"
        session_prompt = (
                introduction
                + "\n" +
                json_format_request
        )

        # # Build the complete session prompt
        # session_prompt = f"{introduction} {json_format_request}"

        return session_prompt

    @staticmethod
    def get_initial_messages(with_instances=None):
        session_prompt = Deduplicator.get_session_prompt(with_instances)
        # print(session_prompt)
        qa_pairs = None
        if with_instances:
            qa_pairs = Deduplicator.convert_instances_into_qa_pairs(with_instances)
        messages = LLMUtil.get_messages(session_prompt, qa_pairs)
        return messages

    @staticmethod
    def question(bugs, with_cots=False):
        # for index, bug in enumerate(bugs):
        #     bug[Placeholder.BUG_ID] = bug.get(Placeholder.BUG_ID, index)
        #     print(bug)
        # Initialize the question with the provided bugs information
        question = f"{bugs}\n"
        # Optionally add a request for chain-of-thought reasoning
        if with_cots:
            question += "\nPlease provide chain-of-thought reasoning before answering."
        return question

    @staticmethod
    def answer(outputs, chains=None):
        if chains:
            return f"{Placeholder.CHAIN_OF_THOUGHTS}: {chains}\n\n" \
                   f"{Placeholder.OUTPUT}: {outputs}"
        return json.dumps(outputs)

    @staticmethod
    def deduplicate(bugs, with_instances=False, with_cots=False,
                    model=LLMUtil.GPT4O_MINI_NAME,
                    temperature=1):
        # if messages is None:
        messages = Deduplicator.get_initial_messages(with_instances)
        # print(messages)
        # LLMUtil.show_messages(messages)
        # extract summary
        question = Deduplicator.question(bugs, with_cots)
        # print(question)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question, messages)
        # print(self.summary_question)
        # input()
        # print(messages)
        answer, cost = LLMUtil.ask_llm_for_chat_completions(messages, model, temperature)
        # answer = Deduplicator.answer(answer)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_ASSISTANT, answer, messages)
        # print(answer)
        answer = json.loads(answer)
        return answer, messages, cost

    @staticmethod
    def get_bugs_from_answer(answer):
        bugs = []
        for one_output in answer[Placeholder.DEDUPLICATOR_OUTPUT]:
            for deduplicate_bug in one_output[Placeholder.DUPLICATE_BUGS]:
                # print(deduplicate_bug)
                if deduplicate_bug:
                    bugs.append(deduplicate_bug)
        # print(len(deduplicate_bugs))
        return bugs

    @staticmethod
    def get_unique_bugs_from_answer(answer):
        unique_bugs = []
        for bugs in answer[Placeholder.DEDUPLICATOR_OUTPUT]:
            unique_bugs.append(bugs[Placeholder.DUPLICATE_BUGS][0])
        return unique_bugs

    @staticmethod
    def get_all_bugs(app, foldername):
        filepath = Path(OUTPUT_DIR, app, foldername)
        # print(filepath)
        json_filenames = FileUtil.find_files_by_extension(filepath, 'json')
        # print(json_filenames)
        json_filenames = sorted(json_filenames)
        # print(json_filenames)
        # print(len(json_filenames))

        output_results = []
        for json_filename in tqdm(json_filenames, ascii=True):
            # print(sec_filename)
            output_result = FileUtil.load_json(json_filename)
            output_results.append(output_result)
        print(len(output_results))

        all_bugs = []
        for output_result in output_results:
            # print(output_result)
            for one_output in output_result[Placeholder.OUTPUT_LIST]:
                try:
                    bugs = one_output[Placeholder.VERIFIER_OUTPUT][Placeholder.BUGS]
                    if bugs:
                        all_bugs.extend(bugs)
                except:
                    print(one_output)
        print(len(all_bugs))
        return all_bugs

    @staticmethod
    def get_the_rest_bugs(deduplicate_output, all_bugs):
        deduplicate_bugs = Deduplicator.get_bugs_from_answer(deduplicate_output)
        # print(deduplicate_bugs)
        # if deduplicate_bugs:
        bugs_in_all, bugs_in_deduplicate = ListUtil.get_diff_by_key_from_two_dict_list(all_bugs, deduplicate_bugs)

        for rest_bug in bugs_in_all:
            print(rest_bug)
        print("###########################")
        for rest_bug in bugs_in_deduplicate:
            print(rest_bug)

        unique_bug_no = int(deduplicate_output[Placeholder.DEDUPLICATOR_OUTPUT][-1][Placeholder.UNIQUE_BUG_NO]) + 1
        for rest_bug in bugs_in_all:
            rest_bug = {
                Placeholder.UNIQUE_BUG_NO: unique_bug_no,
                Placeholder.DUPLICATE_BUGS: [rest_bug]
            }
            unique_bug_no = unique_bug_no + 1
            deduplicate_output[Placeholder.DEDUPLICATOR_OUTPUT].append(rest_bug)

        return deduplicate_output

    @staticmethod
    def deduplicate_bugs(all_bugs, app, model=LLMUtil.GPT4O_MODEL_NAME_WITH_DATE_08, temperature=0):
        # filepath = Path(OUTPUT_DIR, app)
        # filename = f"{app}_deduplicate_bugs"

        answer, messages, cost = Deduplicator.deduplicate(all_bugs, model=model,
                                                          temperature=temperature)

        deduplicate_bugs = Deduplicator.get_bugs_from_answer(answer)
        print(f"Bugs after deduplication: {len(deduplicate_bugs)}")
        try:
            output = Deduplicator.get_the_rest_bugs(answer, all_bugs)
        except Exception as e:
            print(e)
            output = answer
            pass

        deduplicate_bugs = Deduplicator.get_bugs_from_answer(output)
        print(f"Bugs after deduplication and adding the rest: {len(deduplicate_bugs)}")
        return output

    @staticmethod
    def deduplicate_bugs_in_the_loop(all_bugs, app, model=LLMUtil.GPT4O_MODEL_NAME_WITH_DATE_08, temperature=0):
        unique_bug_num = 0
        all_bug_num = len(all_bugs)
        print(f"All bugs as input: {all_bug_num}")

        deduplicator_output = None
        while all_bug_num > unique_bug_num:
            previous_output = deduplicator_output
            all_bug_num = len(all_bugs)
            deduplicator_output = Deduplicator.deduplicate_bugs(all_bugs, app, model, temperature)
            bugs = Deduplicator.get_bugs_from_answer(deduplicator_output)
            print(f"All bugs in the current output: {len(bugs)}")
            if previous_output is not None:
                deduplicator_output = Deduplicator.merge_deduplicator_output_dicts(previous_output, deduplicator_output)
            bugs = Deduplicator.get_bugs_from_answer(deduplicator_output)
            print(f"All bugs in the merged output: {len(bugs)}")
            unique_bugs = Deduplicator.get_unique_bugs_from_answer(deduplicator_output)
            unique_bug_num = len(unique_bugs)
            print(f"Unique bugs in the merged output: {len(bugs)}")

            all_bugs = unique_bugs
        return deduplicator_output

    @staticmethod
    def merge_deduplicator_output_dicts(long_output, short_output):

        new_output = {
            Placeholder.DEDUPLICATOR_OUTPUT: []
        }
        # Process the first dictionary
        for index, item in enumerate(short_output[Placeholder.DEDUPLICATOR_OUTPUT]):
            duplicate_bugs = []

            # if len(item[Placeholder.DUPLICATE_BUGS]) > 1:
            for bug in item[Placeholder.DUPLICATE_BUGS]:
                for long_item in long_output[Placeholder.DEDUPLICATOR_OUTPUT]:
                    if bug in long_item[Placeholder.DUPLICATE_BUGS]:
                        duplicate_bugs.extend(long_item[Placeholder.DUPLICATE_BUGS])
            one_output = {
                Placeholder.UNIQUE_BUG_NO: index,
                Placeholder.DUPLICATE_BUGS: duplicate_bugs
            }
            new_output[Placeholder.DEDUPLICATOR_OUTPUT].append(one_output)
        return new_output


class Filter:
    def __init__(self):
        pass

    @staticmethod
    def convert_instances_into_qa_pairs(bugs):
        # @todo
        qa_pairs = []
        if Placeholder.SCENARIO_MODIFIER_INSTANCES:
            for instance_dict in Placeholder.SCENARIO_MODIFIER_INSTANCES:
                pass
                # # print(instance_dict['bug_id'])
                # bug = bugs.get_bug_by_id(int(instance_dict['bug_id']))
                # question = Verifier.question(bug)
                # answer = Verifier.answer(instance_dict['output'])
                # qa_pairs.append((question, answer))
        return qa_pairs

    @staticmethod
    def get_session_prompt(with_instances=None, format=Placeholder.CLASSIFIER_FORMAT):
        # Basic introduction message for the bug deduplicator
        introduction = (
            f"I am a classifier designed to categorize an issue based on its "
            f"{Placeholder.EXPECTED_BEHAVIORS} and {Placeholder.ACTUAL_BEHAVIORS}. "
            f"If the {Placeholder.EXPECTED_BEHAVIORS} and {Placeholder.ACTUAL_BEHAVIORS} are different, "
            f"it indicates a legitimate issue, and the classifier will return True. "
            f"If the {Placeholder.EXPECTED_BEHAVIORS} and {Placeholder.ACTUAL_BEHAVIORS} are the same "
            f"or convey the same meaning, suggesting there isn't a real issue, the classifier will return False."
        )

        # If a specific format is provided, include a conversion request in the prompt
        json_format_request = ""
        if format:
            json_format_request = f"Please answer in the json format: {format}"
        session_prompt = (
                introduction
                + "\n" +
                json_format_request
        )

        # # Build the complete session prompt
        # session_prompt = f"{introduction} {json_format_request}"

        return session_prompt

    @staticmethod
    def get_initial_messages(with_instances=None):
        session_prompt = Filter.get_session_prompt(with_instances)
        # print(session_prompt)
        qa_pairs = None
        if with_instances:
            qa_pairs = Filter.convert_instances_into_qa_pairs(with_instances)
        messages = LLMUtil.get_messages(session_prompt, qa_pairs)
        return messages

    @staticmethod
    def question(bugs, with_cots=False):
        # for index, bug in enumerate(bugs):
        #     bug[Placeholder.BUG_ID] = bug.get(Placeholder.BUG_ID, index)
        #     print(bug)
        # Initialize the question with the provided bugs information
        question = f"{bugs}\n"
        # Optionally add a request for chain-of-thought reasoning
        if with_cots:
            question += "\nPlease provide chain-of-thought reasoning before answering."
        return question

    @staticmethod
    def answer(outputs, chains=None):
        if chains:
            return f"{Placeholder.CHAIN_OF_THOUGHTS}: {chains}\n\n" \
                   f"{Placeholder.OUTPUT}: {outputs}"
        return json.dumps(outputs)

    @staticmethod
    def classify(bugs, with_instances=False, with_cots=False,
                 model=LLMUtil.GPT4O_MINI_NAME,
                 temperature=1):
        # if messages is None:
        messages = Filter.get_initial_messages(with_instances)
        # print(messages)
        # LLMUtil.show_messages(messages)
        # extract summary
        question = Filter.question(bugs, with_cots)
        # print(question)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_USER, question, messages)
        # print(self.summary_question)
        # input()
        # print(messages)
        answer, cost = LLMUtil.ask_llm_for_chat_completions(messages, model, temperature)
        # answer = Deduplicator.answer(answer)
        messages = LLMUtil.add_role_content_dict_into_messages(LLMUtil.ROLE_ASSISTANT, answer, messages)
        # print(answer)
        answer = json.loads(answer)
        return answer, messages, cost

    # @staticmethod
    # def get_the_rest_bugs(classifier_output, all_bugs):
    #     # @todo
    #     deduplicate_bugs = Deduplicator.get_bugs_from_answer(classifier_output)
    #     valid_bugs = answer[Placeholder.VALID_BUGS]
    #     invalid_bugs = answer[Placeholder.INVALID_BUGS]
    #     bugs_in_all, bugs_in_deduplicate = ListUtil.get_diff_by_key_from_two_dict_list(all_bugs, deduplicate_bugs)
    #
    #     for rest_bug in bugs_in_all:
    #         print(rest_bug)
    #     print("###########################")
    #     for rest_bug in bugs_in_deduplicate:
    #         print(rest_bug)
    #
    #     unique_bug_no = int(deduplicate_output[Placeholder.DEDUPLICATOR_OUTPUT][-1][Placeholder.UNIQUE_BUG_NO]) + 1
    #     for rest_bug in bugs_in_all:
    #         rest_bug = {
    #             Placeholder.UNIQUE_BUG_NO: unique_bug_no,
    #             Placeholder.DUPLICATE_BUGS: [rest_bug]
    #         }
    #         unique_bug_no = unique_bug_no + 1
    #         deduplicate_output[Placeholder.DEDUPLICATOR_OUTPUT].append(rest_bug)
    #
    #     return deduplicate_output

    @staticmethod
    def filter_bugs(app, with_kb, with_oracles, model=LLMUtil.GPT4O_MODEL_NAME_WITH_DATE_08, temperature=0):
        # filepath = Path(OUTPUT_DIR, app)
        filename = f"{app}_classified_bugs"
        if with_kb and with_oracles:
            foldername = 'all'
        elif with_kb and not with_oracles:
            foldername = 'ablation_no_oracles'
            filename = filename + '_no_oracles'
        elif not with_kb and with_oracles:
            foldername = 'ablation_no_kb'
            filename = filename + '_no_kb'
        else:
            foldername = 'ablation_no_kb_no_oracles'
            filename = filename + '_no_kb_no_oracles'
        all_bugs = Deduplicator.get_all_bugs(app, foldername)
        print(f"All bugs in the output: {len(all_bugs)}")
        valid_bugs = []
        invalid_bugs = []

        for bug in tqdm(all_bugs, ascii=True):
            print(bug)
            answer, messages, cost = Filter.classify(bug, model=model,
                                                     temperature=temperature)
            print(answer)
            if answer.get(Placeholder.CLASSIFIER_RESULT) == 'True':
                valid_bugs.append(bug)
            else:
                invalid_bugs.append(bug)

        bugs = {
            Placeholder.VALID_ISSUES: valid_bugs,
            Placeholder.INVALID_ISSUES: invalid_bugs
        }
        # valid_bugs = answer[Placeholder.VALID_ISSUES]
        # invalid_bugs = answer[Placeholder.INVALID_ISSUES]
        # print(f"valid_bugs: {len(valid_bugs)}")
        # print(f"invalid_bugs: {len(invalid_bugs)}")
        # # output = Deduplicator.get_the_rest_bugs(answer, all_bugs)
        # # classified_bugs = Deduplicator.get_bugs_from_answer(output)
        # # print(f"Bugs after deduplication and adding the rest: {len(classified_bugs)}")
        FileUtil.dump_json(Path(OUTPUT_DIR, f"{filename}.json"), bugs)
        # return answer
