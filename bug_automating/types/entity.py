"""
There are entities on the static graph: action, concept and category
"""

import regex as re
import sentence_transformers

from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.list_util import ListUtil
from bug_automating.utils.nlp_util import NLPUtil
from config import ELEMENT_MERGE_THRESHOLD


class Action:
    """
    every time create an action object, it will be added into the category object in categories
    """

    def __init__(self, name, category=None, equivalent=None, opposite=None, alias=None):
        # self.id = id
        self.name = name
        self.category = category
        self.equivalent = equivalent  # name_list (name+alias)
        self.opposite = opposite  # name_list (name+alias)
        # self.relevant = relevant  # name_list (name+alias) for navigate to, switch to, switch back to
        self.alias = alias

        self.equivalent_embedding = None  # name_embedding_list (name+alias embedding)
        self.opposite_embedding = None  # name_embedding_list (name+alias embedding)
        # if categories:
        #     for category in categories:
        #         category.add_action(self)

    def __eq__(self, other):
        return self.name == other.name and self.category == other.category

    def __repr__(self):
        return f'{self.name} - {self.category.name} - {self.equivalent} - {self.opposite} - {self.alias}'
        # if self.category:
        #     return f'{self.name} - {self.category.name}'
        # else:
        #     return f'{self.name} - {self.category}'
        # return f'{self.name} - {self.alias}'

    def __str__(self):
        return f'{self.name} - {self.category.name} - {self.equivalent} - {self.opposite} - {self.alias}'
        # if self.category:
        #     return f'{self.name} - {self.category.name}'
        # else:
        #     return f'{self.name} - {self.category}'
        # return f'{self.name} - {self.alias}'

    def get_action_embedding_list(self):
        self.equivalent_embedding = NLPUtil.SBERT_MODEL.encode(self.equivalent)
        self.opposite_embedding = NLPUtil.SBERT_MODEL.encode(self.opposite)

    @staticmethod
    def merge_name_alias_from_action_name_list(action_name_list):
        """
        merge action_name and action_alias_names into one list
        @param action_name_list: [action_name, action_name, ..., ]
        @type action_name_list: list
        @return: [action_name, action_alias_name, action_alias_name, ..., ]
        @rtype: list
        """
        merge_name_alias_list = list()
        for action_name in action_name_list:
            merge_name_alias_list.append(action_name)
            action_name_alias = Placeholder.ACTION_DICT[action_name]['alias']
            merge_name_alias_list.extend(action_name_alias)

        return merge_name_alias_list

    # @classmethod
    # def extract_action(cls, text):
    #     """
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
    #     @param text:
    #     @type text:
    #     @return:
    #     @rtype:
    #     """
    #     SentUtil.NLP.enable_pipe("merge_noun_chunks")
    #     # print(SentUtil.NLP.pipe_names)
    #     doc = SentUtil.NLP(text)
    #     # extract root verb
    #     root = [token for token in doc if token.head == token]  # verb
    #     adv_left = None  # adv to modify verb advmod 状语
    #     adv_right = None  # adv to modify verb advmod 状语
    #     prt = None  # phrasal verb particle 短语动词助词
    #     prep = None  # prep
    #     obj = None  # obj
    #     concepts = None  # concepts  need to be adjusted
    #     condition = None  # condition
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
    #         obj = [child for child in root.children if child.dep_ == "dobj" or child.dep_ == "nsubjpass"]
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
    #             concepts = re.findall(rf"{Placeholder.Concept}\d+", str(obj), flags=0)
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
    #         root = str(root.lemma_)
    #     if adv_left:
    #         # print(adv.i)
    #         adv_left = str(adv_left)
    #         main_part = adv_left + " " + main_part
    #     if adv_right:
    #         # print(adv.i)
    #         adv_right = str(adv_right)
    #         main_part = main_part + " " + adv_right
    #     if prt:
    #         # print(prt.i)
    #         prt = str(prt)
    #         main_part = main_part + " " + prt
    #     if prep:
    #         # print(prep.i)
    #         prep = str(prep)
    #         main_part = main_part + " " + prep
    #     if obj:
    #         # print(obj.i)
    #         obj = str(obj)
    #         main_part = main_part + " " + obj
    #     condition = Action.extract_condition(text, main_part)
    #     return adv_left, root, adv_right, prt, prep, obj, concepts, condition

    # @classmethod
    # def extract_condition(cls, text, main_part):
    #     condition = text.replace(main_part, "").strip()
    #     is_condition = re.sub('[^A-Za-z0-9]+', ' ', condition).strip()  # remove non-alpha-number and 首尾空格回车等
    #     if not is_condition:
    #         condition = None
    #     return condition

    # @classmethod
    # def categorize_actions_by_concept(cls, text, category_concept_dict, category_action_dict):
    #     """
    #     categorize action by concept
    #     @param text:
    #     @type text:
    #     @param category_concept_dict:
    #     @type category_concept_dict:
    #     @param category_action_dict:
    #     @type category_action_dict:
    #     @return: category_action_dict
    #     @rtype:
    #     """
    #     adv_left_verb_adv_right_prt_prep_obj_concepts = cls.extract_action(text)
    #     print(f"{adv_left_verb_adv_right_prt_prep_obj_concepts}*************************************")
    #     verb = adv_left_verb_adv_right_prt_prep_obj_concepts[1]
    #     concepts = adv_left_verb_adv_right_prt_prep_obj_concepts[6]
    #
    #     if verb:
    #         verb_phrase = verb
    #         if adv_left_verb_adv_right_prt_prep_obj_concepts[0]:
    #             verb_phrase = adv_left_verb_adv_right_prt_prep_obj_concepts[0] + " " + verb_phrase
    #         for index in range(2, 5, 1):
    #             if adv_left_verb_adv_right_prt_prep_obj_concepts[index]:
    #                 verb_phrase = verb_phrase + " " + adv_left_verb_adv_right_prt_prep_obj_concepts[index]
    #                 print(f"{verb_phrase}*************************************")
    #
    #         if concepts:
    #             for concept in concepts:
    #                 concept = SeedExtractor.PLACEHOLDER_DICT[concept]
    #                 # print(type(concept))
    #                 # print(f"****************{concept}****************")
    #                 for category in category_concept_dict.keys():
    #                     if concept in category_concept_dict[category]:
    #                         category_action_dict[category] = category_action_dict.get(category, dict())
    #                         category_action_dict[category][verb_phrase] = category_action_dict[category].get(
    #                             verb_phrase, 0) + 1
    #                         break
    #     # print(category_action_dict)
    #     return category_action_dict


class Concept:
    """
    every time create a concept object, it will be added into the category object
    """

    def __init__(self, id, name, category, alias=None, related_concepts=None):
        self.id = id
        self.name = name
        self.category = category
        self.alias = alias
        self.related_concepts = related_concepts
        category.add_concept(self)
        # self.placeholder = placeholder  # CONCEPT_id

    def __repr__(self):
        return f'{self.id} - {self.name} - {self.category.name} - {self.alias} - {self.related_concepts}'

    def __str__(self):
        return f'{self.id} - {self.name} - {self.category.name} - {self.alias} - {self.related_concepts}'

    def add_alias(self, alia):
        if not self.alias:
            self.alias = set()
        self.alias = set(self.alias)
        self.alias.add(alia)

    def get_placeholder(self):
        """
        need to change or delete
        @return:
        @rtype:
        """
        return f"CONCEPT_{self.id}"  # CONCEPT_id

    def change_category(self, category):
        """
        1. remove concept from previous category (object)
        2. change category (object)
        3. add concept into the new category (object)
        @param category: the new category
        @type category: Category
        @return: None
        @rtype:
        """
        self.category.remove_concept(self)
        self.category = category
        self.category.add_concept(self)


class Category:
    # these dicts need to be removed since they will exist in every category object
    # CATEGORY_CONCEPT_DICT = dict()
    # CATEGORY_ACTION_DICT = dict()
    """
    first, create categories and
    then create concepts and actions
    """

    def __init__(self, name):
        # self.id = id
        self.name = name
        self.concepts = set()
        self.actions = set()  # assign actions (object)

    def add_concept(self, concept):
        self.concepts.add(concept)

    def remove_concept(self, concept):
        self.concepts.remove(concept)

    def add_action(self, action):
        self.actions.add(action)

    def __repr__(self):
        return f'{self.name} - concepts: {self.concepts} - actions: {self.actions}'

    def __str__(self):
        return f'{self.name} - concepts: {self.concepts} - actions: {self.actions}'

    def __eq__(self, other):
        return self.name == other.name

    @staticmethod
    def extract_category(text):
        concept_category_pair_list = list()

        NLPUtil.SPACY_NLP.disable_pipes("merge_noun_chunks", "benepar")

        # print(SentUtil.NLP.pipe_names)
        if len(text) <= 512:
            doc = NLPUtil.SPACY_NLP(text)

            concepts = [token for token in doc if re.fullmatch(rf"{Placeholder.CONCEPT}\d+", str(token), flags=0)]
            if len(concepts) == 0:
                return concept_category_pair_list
            for concept in concepts:
                category = [ancestor for ancestor in concept.ancestors if concept.dep_ == "compound"
                            or concept.dep_ == "amod" or concept.dep_ == "nmod" or concept.dep_ == "nummod"]
                # print(category)
                if len(category) == 0:
                    concept_category_pair_list.append((str(concept), None))
                else:
                    # category consists of multiple words, such as dropdown button, dropdown menu, pop-up, toolbar button
                    category = str(category[0])
                    # print("#############################")
                    # print(text)
                    # print(concept)
                    # print(category)
                    # # print(type(concept))
                    # print("#############################")
                    # re.escape() for strings with escape chars
                    compound_categorys = re.findall(rf"{re.escape(str(concept))}(.*?){re.escape(category)}", text, overlapped=True)
                    # print(compound_categorys)
                    min_compound_category = ""
                    for index, compound_category in enumerate(compound_categorys):
                        if index == 0:
                            min_compound_category = compound_category
                        if len(min_compound_category) > len(compound_category):
                            min_compound_category = compound_category
                    compound_category = min_compound_category
                    # print(compound_category)
                    # print(category)
                    if isinstance(compound_category, str) and isinstance(category, str):
                        category = (compound_category + category).strip()
                    # remove non-alphanumeric string
                    if re.fullmatch(r"^[^a-zA-Z0-9]+$", category, flags=0):
                        category = None

                    concept_category_pair_list.append((str(concept), category))

        return concept_category_pair_list

    @staticmethod
    def get_category_concept_dict(concept_category_dict):
        """
        get CATEGORY_CONCEPT_DICT
        1. rank category by count from all concepts
                                          (concept_category_dict -> category_count_dict, category_count_dict_keys,
                                                    category_rank_dict (key: category, value: rank from 0 to ...))
        2. for each concept, rank category by count in this concept
                            (from concept_category_dict[concept] -> category_dict_keys [category0, category1, ...])
        3. for each concept, if has more than one top-1 categories by count in this concept,
                                                    choose the one with the highest rank by count from all concepts
                             else: choose this one
                              (among categories with the highest category count from concept_category_dict[concept],
                                                    choose the category with the highest rank in category_rank_dict)
        @param concept_category_dict: key-concept, value-dict(category, count)
        @type concept_category_dict: dict
        @return: CATEGORY_CONCEPT_DICT
        @rtype: dict
        """
        # get category-rank dict (rank by count)
        category_count_dict = dict()
        for concept in concept_category_dict.keys():
            for category in concept_category_dict[concept].keys():
                count = concept_category_dict[concept][category]
                category_count_dict[category] = category_count_dict.get(category, 0) + count
        category_count_dict_keys = sorted(category_count_dict, key=category_count_dict.get, reverse=True)
        # print(category_count_dict)
        # print(category_count_dict_keys)
        category_rank_dict = dict()
        for index, key in enumerate(category_count_dict_keys):
            category_rank_dict[key] = category_rank_dict.get(key, index)
        # print(category_rank_dict)
        # get category_concept_dict
        category_concept_dict = dict()
        for concept, category_dict in concept_category_dict.items():
            # if concept == 'about:preferences':
            # print(concept)
            # print(category_dict)
            category_dict_keys = sorted(category_dict, key=category_dict.get, reverse=True)
            # print(category_dict_keys)
            category = category_dict_keys[0]
            for index, category_dict_key in enumerate(category_dict_keys):
                if index > 0 and category_dict[category_dict_key] == category_dict[category_dict_keys[0]]:
                    if category_rank_dict[category_dict_key] < category_rank_dict[category_dict_keys[0]]:
                        category = category_dict_key
            # print(category)
            category_concept_dict[category] = category_concept_dict.get(category, set())
            category_concept_dict[category].add(concept)

        return category_concept_dict

    # @classmethod
    # def get_static_part(cls, category_concept_dict):
    #     """
    #     construct category object and concept object
    #     @return: categories, concepts
    #     @rtype: Category list, Concept list
    #     """
    #     categories = list()
    #     concepts = list()
    #     # for category in Placeholder.CATEGORY_TAG_DICT.keys():
    #     #     categories.append(cls(category))
    #     for category, concepts_in_category in category_concept_dict.items():
    #         category = cls(category)
    #         categories.append(category)
    #         for concept in concepts_in_category:
    #             # # maybe change it back later
    #             # placeholder = SeedExtractor.replace_seed_by_placeholder(f" {concept} ")
    #             # # print(placeholder)
    #             # id = int(placeholder.replace(f"{Placeholder.CONCEPT}", ""))
    #             id = len(concepts)
    #             # print(id)
    #             concept = Concept(id, concept, category)
    #             concepts.append(concept)
    #     return categories, concepts

    @staticmethod
    def get_static_part(category_element_dict=None, category_concept_dict=None):
        """
        1. use Placeholder.CATEGORY_TAG_DICT.keys() to initiate categories (object)
        2. use Placeholder.EXTERNAL_KNOWLEDGE_DICT to construct concepts (object)
        2. if category_element_dict is not None, merge it into categories  #: use this to construct elements (object)
        3. if category_concept_dict is not None, merge it into categories
        4. get actions (object) by use categories (object) and
            Placeholder.ACTION_DICT and
            Placeholder.CATEGORY_ACTION_RELATION_DICT
        @param category_element_dict: category element (string) from ftl and html
        @type category_element_dict: dict
        @param category_concept_dict: category concept (string) from bugs
        @type category_concept_dict: dict
        @return: categories, concepts, actions
        @rtype: object, object, object
        """
        concepts = list()
        categories = Categories(list())
        for category_name in Placeholder.CATEGORY_TAG_DICT.keys():
            category = categories.find_category_by_name(category_name)
            if not category:
                category = Category(category_name)
                categories.categories.append(category)
            if category.name in Placeholder.EXTERNAL_KNOWLEDGE_DICT.keys():
                for concept_name in Placeholder.EXTERNAL_KNOWLEDGE_DICT[category.name]:
                    id = len(concepts)
                    concept = Concept(id, concept_name, category,
                                      Placeholder.EXTERNAL_KNOWLEDGE_DICT[category.name][concept_name]['alias'],
                                      Placeholder.EXTERNAL_KNOWLEDGE_DICT[category.name][concept_name][
                                          'related_concepts'])
                    concepts.append(concept)
            if category.name in category_element_dict.keys():

                for element_name in category_element_dict[category.name]:
                    id = len(concepts)
                    # print(id)
                    concept = Concept(id, element_name, category)
                    concepts.append(concept)
                category_element_dict.pop(category.name, None)
        if category_element_dict:
            category_name = "Others"
            category = categories.find_category_by_name(category_name)
            # if not category:
            #     category = Category(category_name)
            #     categories.categories.append(category)
            for element_name in set(ListUtil.convert_nested_list_to_flatten_list(category_element_dict.values())):
                id = len(concepts)
                concept = Concept(id, element_name, category)
                concepts.append(concept)
        concepts = Concepts(concepts)
        concepts.get_concept_name_list()
        concepts.get_concept_name_embedding_list()

        # for category in categories:
        #     print(category)
        # categories = concepts.merge_concepts(categories, category_element_dict)

        categories = concepts.merge_concepts(categories, category_concept_dict)
        actions = categories.initiate_actions()
        return categories, concepts, actions
        # for category in categories:
        #     print(category)


class Actions:

    def __init__(self, actions):
        self.actions = actions
        self.action_name_list = None
        self.action_name_embedding_list = None
        # self.num = len(categories)

    def __iter__(self):
        for action in self.actions:
            yield action

    def __repr__(self):
        return f'{self.actions}'

    def __str__(self):
        return f'{self.actions}'

    # def __eq__(self, other):
    #     return f'{self.actions}'

    def get_action_name_list(self):
        self.action_name_list = list()
        for action in self.actions:
            self.action_name_list.append(action.name)
        # return self.concept_name_list

    def get_action_name_embedding_list(self):
        self.action_name_embedding_list = NLPUtil.SBERT_MODEL.encode(self.action_name_list)

    def add_action_by_name(self, name):
        """
        @param name: action name
        @type name: string
        @return:
        @rtype:
        """
        return

    def find_action_by_name(self, action_name):
        """

        @param action_name:
        @type action_name:
        @return:
        @rtype:
        """
        for action in self.actions:
            if action.name == action_name:
                return action
            elif action.alias and action_name in action.alias:
                return action
        return None

    # @classmethod
    # def from_action_dict(cls):
    #     """
    #     construct actions (object) from Placeholder.ACTION_DICT
    #     @return:
    #     @rtype:
    #     """
    #     actions = list()
    #     for name, alias in Placeholder.ACTION_DICT.items():
    #         action = Action(name, alias['alias'])
    #         actions.append(action)
    #     return cls(actions)


class Concepts:

    def __init__(self, concepts):
        self.concepts = concepts
        self.concept_name_list = None
        self.concept_name_embedding_list = None
        # self.num = len(categories)

    def __iter__(self):
        for concept in self.concepts:
            yield concept

    def __repr__(self):
        return f'{self.concepts}'

    def __str__(self):
        return f'{self.concepts}'

    # def __eq__(self, other):
    #     return f'{self.concepts}'

    def get_concept_name_list(self):
        self.concept_name_list = list()
        for concept in self.concepts:
            self.concept_name_list.append(concept.name)
        # return self.concept_name_list

    def get_concept_name_embedding_list(self):
        self.concept_name_embedding_list = NLPUtil.SBERT_MODEL.encode(self.concept_name_list)

    # def merge_concepts_by_util_cos(self, categories, category_concept_dict):
    #     """
    #     merge concepts from bugs into concepts from GUI files (merge category_concept_dict into categories)
    #     find category by using category_name
    #     if category is in the categories:
    #         find the category
    #     else:
    #         # Note that category_concept_dict doesn't merge alias
    #         create it
    #         add it into categories
    #     return category
    #     @param categories:
    #     @type categories:
    #     @param category_concept_dict:
    #     @type category_concept_dict:
    #     @return:
    #     @rtype:
    #     """
    #     # merge category_concept_dict into categories
    #     if category_concept_dict:
    #         # # ##########################################################################################################
    #         # # # merge alias in category_concept_dict
    #         # concept_names = list(ListUtil.convert_nested_list_to_flatten_list(category_concept_dict.values()))
    #         # # concept_names_embeddings = NLPUtil.SENTENCE_TRANSFORMER.encode(concept_names, convert_to_tensor=True)
    #         # # logging.warning("Get step cos_sim matrix...")
    #         # # (score, i, j) list
    #         # paraphrases = util.paraphrase_mining(NLPUtil.SENTENCE_TRANSFORMER, concept_names, show_progress_bar=True)
    #         # # logging.warning("merge index_pairs into index_clusters by paraphrases...")
    #         # index_clusters = list()
    #         # for paraphrase in tqdm(paraphrases):
    #         #     score, p_i, p_j = paraphrase
    #         #     if score >= ELEMENT_MERGE_THRESHOLD:
    #         #         index_clusters.append({p_i, p_j})
    #         # index_clusters = ListUtil.merge_sets_with_intersection_in_list(index_clusters)
    #         # concept_clusters = list()
    #         # for index_cluster in index_clusters:
    #         #     concept_cluster = set()
    #         #     for index_concept in index_cluster:
    #         #         concept_cluster.add(concept_names[index_concept])
    #         #     concept_clusters.append(concept_cluster)
    #         # concept_cluster_flags = [False] * len(concept_clusters)
    #         # print(concept_clusters)
    #         # # ##########################################################################################################
    #         category_names = list(Placeholder.CATEGORY_TAG_DICT.keys())
    #         category_names_embeddings = NLPUtil.SBERT_MODEL.encode(category_names, convert_to_tensor=True)
    #
    #         concept_names = list(ListUtil.convert_nested_list_to_flatten_list(category_concept_dict.values()))
    #         concept_names_embeddings = NLPUtil.SBERT_MODEL.encode(concept_names, convert_to_tensor=True)
    #         confirmed_concept_names = list(self.concept_name_list)
    #         confirmed_concept_names_embeddings = NLPUtil.SBERT_MODEL.encode(confirmed_concept_names,
    #                                                                         convert_to_tensor=True)
    #
    #         cossim_pairs_list = NLPUtil.get_pairs_with_cossim_by_decreasing(concept_names_embeddings,
    #                                                                         confirmed_concept_names_embeddings)
    #         # cossims_pair_list = sentence_transformers.util.semantic_search(concept_names_embeddings,
    #         #                                                                confirmed_concept_names_embeddings,
    #         #                                                                top_k=1)
    #
    #         for cossim_pairs in cossim_pairs_list:
    #             cossim_pair = cossim_pairs[0]
    #             concept_name = concept_names[cossim_pair["index"][0]]
    #             confirmed_concept_name = confirmed_concept_names[cossim_pair["index"][1]]
    #             if cossim_pair["score"] >= ELEMENT_MERGE_THRESHOLD:
    #                 if confirmed_concept_name != concept_name:
    #                     confirmed_concept = self.find_concept_by_name(confirmed_concept_name)
    #                     confirmed_concept.add_alias(concept_name)
    #             else:
    #                 # embeddings1 = NLPUtil.SENTENCE_TRANSFORMER.encode(sentences1, convert_to_tensor=True)
    #                 # embeddings2 = NLPUtil.SENTENCE_TRANSFORMER.encode(sentences2, convert_to_tensor=True)
    #                 for key in category_concept_dict.keys():
    #                     if concept_name in category_concept_dict[key]:
    #                         concept_category = key
    #                         concept_category_embeddings = NLPUtil.SBERT_MODEL.encode([concept_category],
    #                                                                                  convert_to_tensor=True)
    #                         cossim_pairs_list = NLPUtil.get_pairs_with_cossim_by_decreasing(concept_category_embeddings,
    #                                                                                         category_names_embeddings)
    #                         if cossim_pairs_list[0][0]["score"] >= ELEMENT_MERGE_THRESHOLD:
    #                             concept_category = categories.find_category_by_name(
    #                                 category_names[cossim_pairs_list[0][0]["index"][1]])
    #                         else:
    #                             concept_category = categories.find_category_by_name("Others")
    #                         # # ##########################################################################################################
    #                         # # # merge alias in category_concept_dict
    #                         # concept_in_alias_flag = False
    #                         # for index, concept_cluster in enumerate(concept_clusters):
    #                         #     if concept_name in concept_cluster:
    #                         #         concept_in_alias_flag = True
    #                         #         if concept_cluster_flags[index]:
    #                         #             for concept_name_alia in concept_cluster:
    #                         #                 concept = self.find_concept_by_name(concept_name_alia)
    #                         #                 if concept:
    #                         #                     concept.add_alias(concept_name)
    #                         #         # break
    #                         #         else:
    #                         #             new_concept = Concept(len(self.concepts), concept_name, concept_category)
    #                         #             self.concepts.append(new_concept)
    #                         #             concept_cluster_flags[index] = True
    #                         #         break
    #                         # if not concept_in_alias_flag:
    #                         #     new_concept = Concept(len(self.concepts), concept_name, concept_category)
    #                         #     self.concepts.append(new_concept)
    #                         # # ##########################################################################################################
    #                         new_concept = Concept(len(self.concepts), concept_name, concept_category)
    #                         self.concepts.append(new_concept)
    #         self.get_concept_name_list()
    #         self.get_concept_name_embedding_list()
    #     return categories

    def merge_concepts(self, categories, category_concept_dict):
        """
        https://www.sbert.net/docs/package_reference/util.html
        sentence_transformers.util.semantic_search

        merge concepts from bugs into concepts from GUI files (merge category_concept_dict into categories)
        find category by using category_name
        if category is in the categories:
            find the category
        else:
            # Note that category_concept_dict doesn't merge alias
            create it
            add it into categories
        return category
        @param categories:
        @type categories:
        @param category_concept_dict:
        @type category_concept_dict:
        @return:
        @rtype:
        """
        # merge category_concept_dict into categories
        if category_concept_dict:
            # # ##########################################################################################################
            # # # merge alias in category_concept_dict
            # concept_names = list(ListUtil.convert_nested_list_to_flatten_list(category_concept_dict.values()))
            # # concept_names_embeddings = NLPUtil.SENTENCE_TRANSFORMER.encode(concept_names, convert_to_tensor=True)
            # # logging.warning("Get step cos_sim matrix...")
            # # (score, i, j) list
            # paraphrases = util.paraphrase_mining(NLPUtil.SENTENCE_TRANSFORMER, concept_names, show_progress_bar=True)
            # # logging.warning("merge index_pairs into index_clusters by paraphrases...")
            # index_clusters = list()
            # for paraphrase in tqdm(paraphrases):
            #     score, p_i, p_j = paraphrase
            #     if score >= ELEMENT_MERGE_THRESHOLD:
            #         index_clusters.append({p_i, p_j})
            # index_clusters = ListUtil.merge_sets_with_intersection_in_list(index_clusters)
            # concept_clusters = list()
            # for index_cluster in index_clusters:
            #     concept_cluster = set()
            #     for index_concept in index_cluster:
            #         concept_cluster.add(concept_names[index_concept])
            #     concept_clusters.append(concept_cluster)
            # concept_cluster_flags = [False] * len(concept_clusters)
            # print(concept_clusters)
            # # ##########################################################################################################
            category_names = list(Placeholder.CATEGORY_TAG_DICT.keys())
            category_names_embeddings = NLPUtil.SBERT_MODEL.encode(category_names, convert_to_tensor=True)

            concept_names = list(ListUtil.convert_nested_list_to_flatten_list(category_concept_dict.values()))
            concept_names_embeddings = NLPUtil.SBERT_MODEL.encode(concept_names, convert_to_tensor=True)
            confirmed_concept_names = list(self.concept_name_list)
            confirmed_concept_names_embeddings = NLPUtil.SBERT_MODEL.encode(confirmed_concept_names,
                                                                            convert_to_tensor=True)

            # cossim_pairs_list = NLPUtil.get_pairs_with_cossim_by_decreasing(concept_names_embeddings,
            #                                                                 confirmed_concept_names_embeddings)
            cossim_pair_list = sentence_transformers.util.semantic_search(concept_names_embeddings,
                                                                           confirmed_concept_names_embeddings,
                                                                           top_k=1)

            for index, cossim_pair in enumerate(cossim_pair_list):
                concept_name = concept_names[index]
                confirmed_concept_name = confirmed_concept_names[cossim_pair[0]["corpus_id"]]
                if cossim_pair[0]["score"] >= ELEMENT_MERGE_THRESHOLD:
                    if confirmed_concept_name != concept_name:
                        confirmed_concept = self.find_concept_by_name(confirmed_concept_name)
                        confirmed_concept.add_alias(concept_name)
                else:
                    # embeddings1 = NLPUtil.SENTENCE_TRANSFORMER.encode(sentences1, convert_to_tensor=True)
                    # embeddings2 = NLPUtil.SENTENCE_TRANSFORMER.encode(sentences2, convert_to_tensor=True)
                    for key in category_concept_dict.keys():
                        if concept_name in category_concept_dict[key]:
                            concept_category = key
                            concept_category_embeddings = NLPUtil.SBERT_MODEL.encode([concept_category],
                                                                                     convert_to_tensor=True)
                            # cossim_pairs_list = NLPUtil.get_pairs_with_cossim_by_decreasing(concept_category_embeddings,
                            #                                                                 category_names_embeddings)
                            cossim_pair_list = sentence_transformers.util.semantic_search(concept_category_embeddings,
                                                                                          category_names_embeddings,
                                                                                          top_k=1)
                            if cossim_pair_list[0][0]["score"] >= ELEMENT_MERGE_THRESHOLD:
                                concept_category = categories.find_category_by_name(
                                    category_names[cossim_pair_list[0][0]["corpus_id"]])
                            else:
                                concept_category = categories.find_category_by_name("Others")
                            # # ##########################################################################################################
                            # # # merge alias in category_concept_dict
                            # concept_in_alias_flag = False
                            # for index, concept_cluster in enumerate(concept_clusters):
                            #     if concept_name in concept_cluster:
                            #         concept_in_alias_flag = True
                            #         if concept_cluster_flags[index]:
                            #             for concept_name_alia in concept_cluster:
                            #                 concept = self.find_concept_by_name(concept_name_alia)
                            #                 if concept:
                            #                     concept.add_alias(concept_name)
                            #         # break
                            #         else:
                            #             new_concept = Concept(len(self.concepts), concept_name, concept_category)
                            #             self.concepts.append(new_concept)
                            #             concept_cluster_flags[index] = True
                            #         break
                            # if not concept_in_alias_flag:
                            #     new_concept = Concept(len(self.concepts), concept_name, concept_category)
                            #     self.concepts.append(new_concept)
                            # # ##########################################################################################################
                            new_concept = Concept(len(self.concepts), concept_name, concept_category)
                            self.concepts.append(new_concept)
            self.get_concept_name_list()
            self.get_concept_name_embedding_list()
        return categories

    def add_concept_by_name(self, name):
        """
        @param name: concept name
        @type name: string
        @return:
        @rtype:
        """
        return

    def find_concept_by_name(self, concept_name):
        """

        @param concept_name:
        @type concept_name:
        @return:
        @rtype:
        """
        for concept in self.concepts:
            if concept.name == concept_name:
                return concept
            elif concept.alias and concept_name in concept.alias:
                return concept
        return None


class Categories:
    def __init__(self, categories):
        self.categories = categories
        # self.num = len(categories)

    def __iter__(self):
        for category in self.categories:
            yield category

    def __repr__(self):
        return f'{self.categories}'

    def __str__(self):
        return f'{self.categories}'

    # def __eq__(self, other):
    #     return f'{self.categories}'

    def find_category_by_name(self, name):
        """
        find category by using category_name
        if category is in the categories:
            find the category
        else:
            category = None
            # create it
            # add it into categories
        return category
        @param name:
        @type name:
        @return:
        @rtype:
        """
        if self.categories:
            for category in self.categories:
                if category.name == name:
                    return category

        # category = Category(name)
        # self.categories.append(category)
        # return category
        return None

    def initiate_actions(self):
        """
        get actions from Placeholder.CATEGORY_ACTION_RELATION_DICT and Placeholder.ACTION_DICT
        @return: categories with actions and actions
        @rtype: actions (object)
        """
        actions = list()
        for category in self.categories:
            category_actions = list()
            action_relation_dict = Placeholder.CATEGORY_ACTION_RELATION_DICT[category.name]
            for action_name, relation_dict in action_relation_dict.items():
                action = Action(action_name, category)
                action.alias = Placeholder.ACTION_DICT[action_name]['alias']

                equivalent = list()
                equivalent.append(action.name)
                equivalent.extend(action.alias)
                equivalent.extend(Action.merge_name_alias_from_action_name_list(relation_dict['equivalent']))
                action.equivalent = equivalent

                opposite = list()
                opposite.extend(Action.merge_name_alias_from_action_name_list(relation_dict['opposite']))
                action.opposite = opposite
                # get action.equivalent_embedding and action.opposite_embedding
                action.get_action_embedding_list()
                category_actions.append(action)
                actions.append(action)
            category.actions = Actions(category_actions)

        return Actions(actions)

    def get_concepts(self):
        """
        get concepts from categories
        @return: concepts
        @rtype: object
        """
        concepts = list()
        for category in self.categories:
            concepts.extend(list(category.concepts))
        return Concepts(concepts)

    # def get_actions(self):
    #     actions = list()
    #     for category in self.categories:
    #         actions.extend(list(category.actions))
    #     return concepts
