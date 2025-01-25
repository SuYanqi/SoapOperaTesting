from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.types._data import _Data


# class Argument:
#     def __init__(self, argument_object, name, argument_type=None):
#         self.object = argument_object  # step or check_item includes this argument
#         self.name = name
#         self.type = argument_type
#
#     def __repr__(self):
#         # if NLPUtil.is_url(self.id):
#         #     bug_id = self.bug.id
#         # else:
#         #     bug_id = f'{MOZILLA_BUG_LINK}{self.bug.id}'
#         return f'{self.object} - {self.name} - {self.type}' \
#             # f' - {self.cluster_index}'
#
#     def __str__(self):
#         # if NLPUtil.is_url(self.id):
#         #     bug_id = self.bug.id
#         # else:
#         #     bug_id = f'{MOZILLA_BUG_LINK}{self.bug.id}'
#         return f'{self.object} - {self.name} - {self.type}' \
#             # f' - {self.cluster_index}'


# class CheckItem:
#     def __init__(self, text, arguments=None):
#         self.attached_steps = None  # steps including this check item
#         self.text = text
#         self.arguments = arguments
#
#     def __repr__(self):
#         # if NLPUtil.is_url(self.id):
#         #     bug_id = self.bug.id
#         # else:
#         #     bug_id = f'{MOZILLA_BUG_LINK}{self.bug.id}'
#         return f'{self.text} - {self.arguments}' \
#             # f' - {self.cluster_index}'
#
#     def __str__(self):
#         # if NLPUtil.is_url(self.id):
#         #     bug_id = self.bug.id
#         # else:
#         #     bug_id = f'{MOZILLA_BUG_LINK}{self.bug.id}'
#         return f'{self.text} - {self.arguments}' \
#             # f' - {self.cluster_index}'
from config import TO_DICT_OMIT_ATTRIBUTES


class CheckItem(_Data):
    def __init__(self, text, cluster_index=None, bug=None):
        # self.attached_steps = None  # steps including this check item
        super().__init__()
        self.bug = bug
        self.text = text
        self.cluster_index = cluster_index

    def __repr__(self):
        return f'{self.bug.id} - {self.text} - {self.cluster_index}'

    def __str__(self):
        return f'{self.bug.id} - {self.text} - {self.cluster_index}'

    @classmethod
    def from_dict(cls, step_dict, bug=None):
        return cls(step_dict[Placeholder.STEP], step_dict[Placeholder.CLUSTER_INDEX], bug)


class Action(_Data):
    def __init__(self, text, scroll_direction=None):
        # self.id = id
        # self.bug = bug
        super().__init__()
        self.text = text
        self.scroll_direction = scroll_direction

    def __repr__(self):
        return f'{self.text} - {self.scroll_direction}'

    def __str__(self):
        return f'{self.text} - {self.scroll_direction}'

    def __eq__(self, other):
        return self.text == other.text and self.scroll_direction == self.scroll_direction

    def __hash__(self):
        return hash(str(self))

    @classmethod
    def from_dict(cls, text, scroll_direction=None):
        """
        return preconditions
        """
        return cls(text, scroll_direction)


class Element(_Data):
    def __init__(self, text, coordinate, input=None, category=None):
        # self.id = id
        # self.bug = bug
        super().__init__()
        self.text = text
        self.coordinate = coordinate
        self.input = input
        self.category = category

    def __repr__(self):
        return f'{self.text} - {self.coordinate} - {self.input} - {self.category}'

    def __str__(self):
        return f'{self.text} - {self.coordinate} - {self.input} - {self.category}'

    def __eq__(self, other):
        return self.text == other.text and self.coordinate == self.coordinate and self.input == self.input

    def __hash__(self):
        return hash(str(self))

    @classmethod
    def from_dict(cls, text, coordinate, input=None, category=None):
        return cls(text, coordinate, input, category)


class Step(_Data):
    def __init__(self, text, check_items=None, prev_step=None, next_step=None, bug=None, id=None):

        super().__init__()
        self.bug = bug
        self.id = id
        self.text = text
        # self.sub_steps = []
        # self.action = None
        # self.element = None
        # self.arguments = arguments
        # self.type = step_type  # maybe will remove: because all steps are about operation
        self.check_items = check_items  # non-operational steps are added into step's check_items

        self.prev_step = prev_step  # step object
        self.next_step = next_step

        self.cluster_index = None

    def __repr__(self):
        check_items = ""
        for check_item in self.check_items:
            check_items = check_items + f"\t{check_item}\n"
        return f'{self.bug.id} - {self.id} - {self.text} ' \
               f'- {self.cluster_index}\n - {check_items}'

    def __str__(self):
        check_items = ""
        for check_item in self.check_items:
            check_items = check_items + f"\t{check_item}\n"
        return f'{self.bug.id} - {self.id} - {self.text} ' \
               f'- {self.cluster_index}\n - {check_items}'

    def __eq__(self, other):
        # todo
        return self.text == other.text

    def __hash__(self):
        return hash(str(self))

    @classmethod
    def from_dict(cls, step_dict, prev_step=None, bug=None):
        """
        return preconditions
        """
        step_type = step_dict[Placeholder.STEP_TYPE]
        if step_type == Placeholder.STEP_TYPE_ACTION:
            step = cls(step_dict[Placeholder.STEP], [], prev_step, bug=bug)
            step.cluster_index = step_dict[Placeholder.CLUSTER_INDEX]
            if prev_step:
                prev_step.next_step = step
            return step
        else:
            check_item = CheckItem.from_dict(step_dict, bug)
            if prev_step:
                prev_step.check_items.append(check_item)
                return None
            else:
                # this is a precondition
                return check_item
                # logging.warning(f"BugID: {bug.id}. CheckItem is the first step: {step_dict}")
        # return step

    def is_in_the_same_path(self, step):
        """
        self and step is in the same path or not
        from self forward search
        from self back search
        @param step: the step need to be compared with self_step
        @type step: Step
        @return: true or false
        @rtype: boolean
        """
        if step is None:
            return False
        prev_step = self
        while prev_step is not None:
            if prev_step == step:
                return True
            else:
                prev_step = prev_step.prev_step
        next_step = self.next_step
        while next_step is not None:
            if next_step == step:
                return True
            else:
                next_step = next_step.next_step
        return False

    # @staticmethod
    # def extract_action_target_condition_concept_tuple(text):
    #     """
    #     Have session store enabled.  -> verb + nsubj or nsubjpass
    #     Click the CONCEPT_13 button. -> verb + obj
    #     Go to CONCEPT_2              -> verb + prep + pobj
    #     Scroll down the CONCEPT_33.  -> verb + prt + obj
    #     Scroll down to CONCEPT_29.   -> verb + prt + prep + pobj
    #     Focus back to the CONCEPT_2 page. -> verb + advmod + prep + pobj
    #     I right clicked the Password field -> advmod + verb + dobj
    #     Right-click on the password -> advmod + punct + verb + prep + pobj
    #     Right click on the website address link. -> intj + verb + prep + pobj
    #     Observe what button is focused on.
    #     Try to see a password, by clicking the "eye", or copy it by clicking "copy".
    #     Move the mouse away, hover over it again;
    #     Middle click on the CONCEPT_23 and CONCEPT_22 buttons.
    #     *************************************************
    #     for obj:
    #     Click on one of the saved logins that has a very long username.
    #     Click, on, one, []
    #     Select any of the saved logins.
    #     Select, None, any, []
    #     In CONCEPT_6 set identity.fxaccounts.enabled = false.
    #     set, None, false, []
    #     Observe the “Go to <webite_name>” link.
    #     Observe, None, Go, []
    #     Look at the "Created/Last modified/Last used" area
    #     Look, at, modified, []
    #     Open the Beta 70.0b3 Italian build with the profile from prerequisites.
    #     Open, None, Italian, []
    #     Select CONCEPT_13
    #     Login to sync & logins data;
    #     click logins and passwords
    #     Delete by clicking the Remove button.
    #     visit URL_4
    #     @param doc:
    #     @type doc:
    #     @param text:
    #     @type text:
    #     @return:
    #     @rtype:
    #     """
    #     NLPUtil.SPACY_NLP.enable_pipe("merge_noun_chunks")
    #     # SpacyModel.NLP.disable_pipes("benepar")
    #     # logging.warning(SpacyModel.NLP.pipe_names)
    #     # print(SentUtil.NLP.pipe_names)
    #     # if not doc:
    #     text = SeedExtractor.replace_seed_by_placeholder(text)
    #     doc = NLPUtil.SPACY_NLP(text)
    #     # extract root verb
    #     root = [token for token in doc if token.head == token]  # verb
    #     adv_left = None  # adv to modify verb advmod 状语
    #     adv_right = None  # adv to modify verb advmod 状语
    #     prt = None  # phrasal verb particle 短语动词助词
    #     prep = None  # prep
    #     obj = None  # obj
    #     concepts_in_object = []
    #     verb_phrase = None
    #     # concepts = None  # concepts  need to be adjusted
    #     # conditions = list()  # condition
    #     if root:
    #         root = root[0]
    #         # extract adverbial modifier
    #         adv = [child for child in root.children if child.dep_ == "intj" or child.dep_ == "advmod"]
    #         if adv:
    #             adv = adv[0]
    #             if adv.i == root.i - 1:
    #                 adv_left = adv
    #             elif adv.i == root.i + 1:
    #                 adv_right = adv
    #         # extract dobj
    #         obj = [child for child in root.children if
    #                child.dep_ == "dobj" or child.dep_ == "nsubjpass" or child.dep_ == "nsubj"]
    #         if not obj:
    #             # extract verb [prep]
    #             prep = [child for child in root.children if child.dep_ == "prep"]
    #             # get the object of the action (root)
    #             if prep:
    #                 # extract prep [obj]
    #                 prep = prep[0]
    #                 obj = [child for child in prep.children if child.dep_ == "pobj"]
    #
    #         # extract phrasal verb particle
    #         prt = [child for child in root.children if child.dep_ == "prt"]
    #         if prt:
    #             prt = prt[0]
    #         else:
    #             prt = None
    #         # print(verb_comp)
    #         if adv_right and not obj and not prep:
    #             prep = [child for child in adv_right.children if child.dep_ == "prep"]
    #             # get the object of the action (root)
    #             if prep:
    #                 # extract prep [obj]
    #                 prep = prep[0]
    #                 obj = [child for child in prep.children if child.dep_ == "pobj"]
    #         # concepts = None
    #         if obj:
    #             obj = obj[0]
    #             # extract concepts from obj only
    #             concepts_in_object = re.findall(rf"{Placeholder.CONCEPT}\d+", str(obj), flags=0)
    #         else:
    #             obj = None
    #     else:
    #         root = None
    #     # concepts = re.findall(rf"{Placeholder.Concept}\d+", str(text), flags=0)
    #     # print(obj)
    #     # print(concepts)
    #     main_part = ""
    #
    #     if root:
    #         # print(root.i)
    #         main_part = str(root)
    #         verb_phrase = str(root.lemma_)
    #     if adv_left:
    #         # print(adv.i)
    #         # adv_left = str(adv_left)
    #         main_part = str(adv_left) + " " + main_part
    #         verb_phrase = str(adv_left.lemma_) + " " + verb_phrase
    #     if adv_right:
    #         # print(adv.i)
    #         main_part = main_part + " " + str(adv_right)
    #         verb_phrase = verb_phrase + " " + str(adv_right.lemma_)
    #     if prt:
    #         # print(prt.i)
    #         # prt = str(prt)
    #         main_part = main_part + " " + str(prt)
    #         verb_phrase = verb_phrase + " " + str(prt.lemma_)
    #     if prep:
    #         # print(prep.i)
    #         # prep = str(prep)
    #         main_part = main_part + " " + str(prep)
    #         verb_phrase = verb_phrase + " " + str(prep.lemma_)
    #     if obj:
    #         # print(obj.i)
    #         obj = str(obj)
    #         obj = SeedExtractor.replace_placeholder_by_seed(obj)[0]
    #         main_part = main_part + " " + obj
    #     concepts = re.findall(rf"{Placeholder.CONCEPT}\d+", text, flags=0)
    #     if concepts:
    #         for index, concept in enumerate(concepts):
    #             concepts[index] = SeedExtractor.replace_placeholder_by_seed(concept)[0]
    #     if concepts_in_object:
    #         for index, concept in enumerate(concepts_in_object):
    #             concepts_in_object[index] = SeedExtractor.replace_placeholder_by_seed(concept)[0]
    #
    #     text = SeedExtractor.replace_placeholder_by_seed(text)[0]
    #     conditions = Step.extract_condition(text, main_part)
    #     # condition = Step.extract_condition(text, verb_phrase, obj)
    #
    #     return verb_phrase, obj, conditions, concepts, concepts_in_object
    #
    # @classmethod
    # def extract_condition(cls, text, main_part):
    #     # SpacyModel.NLP.disable_pipes("benepar")
    #     # logging.warning(SpacyModel.NLP.pipe_names)
    #     conditions = list()
    #     # print(main_part)
    #     # use click to replace Verb_phrase, use button replace obj for pps extraction
    #     text = text.replace(main_part, "click button")
    #     text = SeedExtractor.replace_seed_by_placeholder(text)
    #
    #     doc = NLPUtil.SPACY_NLP(text)
    #     prep_phrases = SentUtil.extract_prep_phrases(doc)
    #     for pp in prep_phrases:
    #         pp = SeedExtractor.replace_placeholder_by_seed(str(pp))[0]
    #         conditions.append(pp)
    #
    #     if not conditions:
    #         conditions = None
    #     return conditions

    # @classmethod
    # def extract_condition(cls, text, main_part):
    #     print(main_part)
    #     condition = text.replace(main_part, "")
    #     # is_condition = re.sub('[^A-Za-z0-9]+', ' ', condition).strip()  # remove non-alpha-number and 首尾空格回车等
    #     # remove non-alphanumeric characters at the beginning or end of a string
    #     condition = re.sub(r"^\W+|\W+$", "", condition)
    #     if not condition:
    #         condition = None
    #     return condition


#
# class Example:
#     """
#     dynamically add attributes to object at runtime
#     """
#
#     def __init__(self):
#         pass
#
#     def __repr__(self):
#         attributes_dict = vars(self)
#         # Alternatively, you can use obj.__dict__
#         # attributes_dict = obj.__dict__
#
#         # Traversing all attributes
#         attribute_name_value_str = ''
#         for attribute_name, attribute_value in attributes_dict.items():
#             attribute_name_value_str = attribute_name_value_str + f"{attribute_name}: {attribute_value}\n"
#         return attribute_name_value_str
#
#     def __str__(self):
#         attributes_dict = vars(self)
#         # Alternatively, you can use obj.__dict__
#         # attributes_dict = obj.__dict__
#
#         # Traversing all attributes
#         attribute_name_value_str = ''
#         for attribute_name, attribute_value in attributes_dict.items():
#             attribute_name_value_str = attribute_name_value_str + f"{attribute_name}: {attribute_value}\n"
#         return attribute_name_value_str
#
#     @classmethod
#     def from_dict(cls, example_dict):
#         """
#         # Dynamic attribute access
#         dynamic_value = getattr(obj, attribute_name)
#         """
#         example = cls()
#         for attribute, value in example_dict.items():
#             setattr(example, attribute, value)
#         return example
#
#     def get_attribute_value_by_name(self, attr_name):
#         return getattr(self, attr_name)


class Scenario(_Data):
    def __init__(self, prerequisites=None, summary=None, steps=None, bug=None):
        super().__init__()
        self.bug = bug
        self.summary = summary
        self.prerequisites = prerequisites
        self.steps = steps
        # self.expected_results = expected_results
        # self.actual_results = actual_results
        # self.examples = examples
        # self.notes = notes
        # self.attachments = attachments
        # self.variations = variations
        # self.tasks = tasks

    def __repr__(self):
        # @todo
        return f'{self.bug}' \
               f'{Placeholder.SCENARIO}: \n' \
               f'\t{Placeholder.SUMMARY}: {self.summary}\n' \
               f'\t{Placeholder.STEPS}: {self.steps}'

    def __str__(self):
        # @todo
        return f'{self.bug}' \
               f'{Placeholder.SCENARIO}: \n' \
               f'\t{Placeholder.SUMMARY}: {self.summary}\n' \
               f'\t{Placeholder.STEPS}: {self.steps}'

    @classmethod
    def from_dict(cls, scenario_dict, bug=None):
        # scenario = cls([], scenario_dict[Placeholder.SUMMARY], [])
        steps = []
        preconditions = scenario_dict[Placeholder.PRECONDITIONS]
        for step_dict in scenario_dict[Placeholder.STEPS]:
            prev_step = None
            if steps:
                prev_step = steps[-1]
            step = Step.from_dict(step_dict, prev_step, bug)
            if hasattr(step, 'check_items'):
                steps.append(step)
            elif step:
                preconditions.append(step)
        for index, step in enumerate(steps):
            step.id = index
        if scenario_dict[Placeholder.SUMMARY] is None:
            scenario_dict[Placeholder.SUMMARY] = bug.summary
        return cls(preconditions, scenario_dict[Placeholder.SUMMARY], steps, bug)

    def get_action_step_dicts(self):
        TO_DICT_OMIT_ATTRIBUTES.add('check_items')
        action_steps = []
        for step in self.steps:
            # step = {Placeholder.STEP_NO: step.id,
            #         Placeholder.STEP: step.text,
            #         Placeholder.STEP_CLUSTER: step.cluster_index}
            action_steps.append(step.to_dict())
        return action_steps

    def get_step_by_cluster_index(self, cluster_index):
        if cluster_index:
            for step in self.steps:
                if step.cluster_index == cluster_index:
                    return step
        return None

    def get_steps_between_start_and_end_cluster_index(self, start_cluster_index, end_cluster_index):
        """
           A -> B -> C
           return True, if scenario has the steps with start_cluster_index and end_cluster_index
           start_cluster_index can be None, and if end_step and end_step.id != 0
        """
        start_step = self.get_step_by_cluster_index(start_cluster_index)
        end_step = self.get_step_by_cluster_index(end_cluster_index)
        if start_cluster_index is None:
            if end_step and end_step.id != 0:
                return self.steps[0: end_step.id+1]
        else:
            # start_step (A) and end_step (B) not A -> B, must have at least 1 step inside, like A->B->C
            if start_step and end_step and start_step.id + 1 < end_step.id:
                return self.steps[start_step.id: end_step.id+1]
        return None


class Description(_Data):

    def __init__(self, text=None, scenarios=None, attachments=None):
        super().__init__()
        self.text = text
        # self.backgrounds = backgrounds
        self.scenarios = scenarios
        # self.steps_to_reproduce = steps_to_reproduce
        # self.expected_results = expected_results
        # self.actual_results = actual_results
        # self.notes = notes
        self.attachments = attachments
        # self.variations = variations

    def __repr__(self):
        return f'{self.text}'

    def __str__(self):
        return f'{self.text}'

    def get_scenarios(self, scenario_dicts, bug=None):
        self.scenarios = []
        for scenario_dict in scenario_dicts:
            scenario = Scenario.from_dict(scenario_dict, bug)
            if scenario:
                self.scenarios.append(scenario)

    @classmethod
    def from_text(cls, text, scenario_dicts=None):
        desc = cls(text)
        if scenario_dicts:
            desc.get_scenarios(scenario_dicts)
        # scenarios = []
        # for scenario_dict in scenario_dicts:
        #     scenario = Scenario.from_dict(scenario_dict)
        #     if scenario:
        #         scenarios.append(scenario)

        return desc
