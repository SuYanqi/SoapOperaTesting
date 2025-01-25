class FormatUtil:
    MAIN_CHOOSE_BY_ELEMENT = 1
    MAIN_CHOOSE_BY_COSSIM = 2
    MAIN_CHOOSE_BY_CLUSTER_INDEX = 3
    MAIN_CHOOSE_BY_BUG_ID = 4
    MAIN_CHOOSE_BY_EXIT = 5

    @staticmethod
    def format_bugkg_main_gui():
        main_gui = "Welcome to BugKG!!! (⑅˃◡˂⑅)\n" \
                   "———————————————————————————————————————\n" \
                   f"{FormatUtil.MAIN_CHOOSE_BY_ELEMENT}. Search the BugKG by Element\n" \
                   f"{FormatUtil.MAIN_CHOOSE_BY_COSSIM}. Search the BugKG by CosSim \n" \
                   f"{FormatUtil.MAIN_CHOOSE_BY_CLUSTER_INDEX}. Search the cluster by cluster_index \n" \
                   f"{FormatUtil.MAIN_CHOOSE_BY_BUG_ID}. Search the relevant bugs by bug_id\n" \
                   f"{FormatUtil.MAIN_CHOOSE_BY_EXIT}. Exit\n" \
                   "———————————————————————————————————————"
        print(main_gui)
        choose = int(input(f"Please choose ({FormatUtil.MAIN_CHOOSE_BY_ELEMENT} or {FormatUtil.MAIN_CHOOSE_BY_COSSIM}"
                           f" or {FormatUtil.MAIN_CHOOSE_BY_CLUSTER_INDEX} or {FormatUtil.MAIN_CHOOSE_BY_BUG_ID} or "
                           f"{FormatUtil.MAIN_CHOOSE_BY_EXIT}): "))
        return choose

    # @staticmethod
    # def format_cluster(cluster):
    #     """
    #     convert a cluster (Step list) into a json
    #     @param cluster:
    #     @type cluster:
    #     @return:
    #     @rtype:
    #     """
    #     cluster_json = {
    #         'bug_id_list': [],
    #         'step_id_list': [],
    #         'precondition_list': [],
    #         'step_list': [],
    #         'expected_result_list': [],
    #         'actual_result_list': []
    #     }
    #     for step in cluster:
    #         cluster_json['bug_id_list'].append(f"https://bugzilla.mozilla.org/show_bug.cgi?id={step.bug.id}")
    #         cluster_json['step_id_list'].append(int(step.id))
    #
    #         if int(step.id) == 0:
    #             cluster_json['precondition_list'].append(step.bug.description.prerequisites)
    #         else:
    #             cluster_json['precondition_list'].append(None)
    #         cluster_json['step_list'].append(step.text)
    #         if int(step.id) == len(step.bug.description.steps_to_reproduce) - 1:
    #             cluster_json['expected_result_list'].append(step.bug.description.expected_results)
    #             cluster_json['actual_result_list'].append(step.bug.description.actual_results)
    #         else:
    #             cluster_json['expected_result_list'].append(None)
    #             cluster_json['actual_result_list'].append(None)
    #     return cluster_json

    @staticmethod
    def format_cluster(cluster):
        """
        convert a cluster (Step list) into a json
        @param cluster:
        @type cluster:
        @return:
        @rtype:
        """

        max_prev_steps_to_reproduce_length = 0
        max_next_steps_to_reproduce_length = 0
        max_prev_steps_to_reproduce_step_id = 0
        # max_next_steps_to_reproduce_step_id = None
        for step in cluster:
            steps_to_reproduce_length = len(step.section_answer.description.all_steps)
            if max_prev_steps_to_reproduce_length < int(step.id):
                max_prev_steps_to_reproduce_length = int(step.id)
                max_prev_steps_to_reproduce_step_id = int(step.id)
            if max_next_steps_to_reproduce_length < steps_to_reproduce_length - int(step.id) - 1:
                max_next_steps_to_reproduce_length = steps_to_reproduce_length - int(step.id) - 1
                # max_next_steps_to_reproduce_step_id = int(step.id)
        # max_steps_to_reproduce_step_id
        cluster_json = {
            'bug_id': [],
            'summary': [],
            'precondition': [],
            # 'step_list': [],
            # 'expected_result_list': [],
            # 'actual_result_list': []
        }
        for n in range(max_prev_steps_to_reproduce_length + 1 + max_next_steps_to_reproduce_length):
            cluster_json[f'step_{n}'] = cluster_json.get(f'step_{n}', [])
        cluster_json['expected_result'] = cluster_json.get('expected_result', [])
        cluster_json['actual_result'] = cluster_json.get('actual_result', [])

        for step in cluster:
            cluster_json['bug_id'].append(f"https://bugzilla.mozilla.org/show_bug.cgi?id={step.section_answer.id}")
            cluster_json['summary'].append(step.section_answer.summary)

            cluster_json['precondition'].append(step.section_answer.description.prerequisites)
            steps_to_reproduce_length = len(step.section_answer.description.all_steps)
            step_gap = max_prev_steps_to_reproduce_step_id - int(step.id)
            for n in range(max_prev_steps_to_reproduce_length + 1 + max_next_steps_to_reproduce_length):
                if steps_to_reproduce_length > n - step_gap >= 0:
                    cluster_json[f'step_{n}'].append(f"{step.section_answer.description.all_steps[n - step_gap].cluster_index}\t"
                                                     f"{step.section_answer.description.all_steps[n - step_gap].text}")
                else:
                    cluster_json[f'step_{n}'].append(None)

            cluster_json['expected_result'].append(step.section_answer.description.expected_results)
            cluster_json['actual_result'].append(step.section_answer.description.actual_results)
        return cluster_json

    @staticmethod
    def format_bug_list(bug_list):
        """
        convert a bug_list (bug (Bug) list) into a json
        @param bug_list: bug (Bug) list
        @type: list
        @return: bug_list_json
        @rtype: json
        """

        max_steps_to_reproduce_length = 0

        for bug in bug_list:
            steps_to_reproduce_length = len(bug.description.all_steps)
            if max_steps_to_reproduce_length < steps_to_reproduce_length:
                max_steps_to_reproduce_length = steps_to_reproduce_length

        bug_list_json = {
            'bug_id': [],
            'summary': [],
            'precondition': [],
            # 'step_list': [],
            # 'expected_result_list': [],
            # 'actual_result_list': []
        }
        for n in range(max_steps_to_reproduce_length):
            bug_list_json[f'step_{n}'] = bug_list_json.get(f'step_{n}', [])
        bug_list_json['expected_result'] = bug_list_json.get('expected_result', [])
        bug_list_json['actual_result'] = bug_list_json.get('actual_result', [])

        for bug in bug_list:
            bug_list_json['bug_id'].append(f"https://bugzilla.mozilla.org/show_bug.cgi?id={bug.id}")
            bug_list_json['summary'].append(bug.summary)

            bug_list_json['precondition'].append(bug.description.prerequisites)

            for n in range(max_steps_to_reproduce_length):
                if n < len(bug.description.all_steps):
                    bug_list_json[f'step_{n}'].append(
                        f"{bug.description.all_steps[n].cluster_index}\t"
                        f"{bug.description.all_steps[n].text}")
                else:
                    bug_list_json[f'step_{n}'].append(None)

            bug_list_json['expected_result'].append(bug.description.expected_results)
            bug_list_json['actual_result'].append(bug.description.actual_results)
        return bug_list_json
