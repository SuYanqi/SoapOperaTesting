import logging
import re
from pathlib import Path

from bs4 import BeautifulSoup
from tqdm import tqdm

from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil
from bug_automating.utils.nlp_util import NLPUtil


class Element:
    """
    element from FTL files
    get element category from FTL and html
    """

    def __init__(self, id, name=None, attributes=None, comment=None, category=None):
        self.id = id
        self.name = name
        self.attributes = attributes
        self.comment = comment
        self.category = category

        self.names_from_attributes = None

        self.get_name_from_attributes()

    def __repr__(self):
        # if self.category:
        #     return f'{self.name} - {self.category.name}'
        # else:
        #     return f'{self.name} - {self.category}'
        return f'{self.id} - {self.name} - {self.attributes} - {self.comment} - {self.names_from_attributes} ' \
               f'- {self.category}'

    def __str__(self):
        # if self.category:
        #     return f'{self.name} - {self.category.name}'
        # else:
        #     return f'{self.name} - {self.category}'
        return f'{self.id} - {self.name} - {self.attributes} - {self.comment} - {self.names_from_attributes} ' \
               f'- {self.category}'

    @classmethod
    def from_dict(cls, element_dict):
        """
        get elements from ftl
        :param cls:
        :return:
        @param element_dict:
        @type element_dict:
        """
        id = None
        name = None
        attributes = None
        comment = None
        for key in element_dict.keys():
            if key == "id":
                # cls.id = Element.get_id(element_dict['id'])
                id = element_dict['id']['name']
            elif key == "value":
                # if element_dict['value']:
                #  ignore len(elements) > 1
                name = Element.get_name(element_dict['value'])
            elif key == "attributes":
                attributes = Element.get_attributes(element_dict['attributes'])
            elif key == "comment":
                comment = Element.get_comment(element_dict['comment'])

        if id:
            return cls(id, name, attributes, comment)
        return None

    # @staticmethod
    # def get_id(id_dict):
    #     name = ''
    #     return name
    def get_name_from_attributes(self):
        names = list()
        if self.name is None and self.attributes:
            for attribute in self.attributes:
                for id in Placeholder.ATTRIBUTE_IDS:

                    if id in attribute.id:
                        if attribute.name:
                            names.append(attribute.name)
        if names:
            self.names_from_attributes = names

    @staticmethod
    def get_name(name_dict):
        """
        from key: value dict to extract name (TextElement)
        @param name_dict:
        @type name_dict:
        @return:
        @rtype:
        """
        name = None
        if name_dict:
            key = "elements"
            if key in name_dict.keys():
                elements_dict = name_dict[key]
                if len(elements_dict) == 1:
                    key = 'value'
                    if key in elements_dict[0].keys():
                        name = elements_dict[0][key]
                # else:

                # for element in name_dict['elements']:
                #     for key in element.keys():
                #         if key == "value":
                #             name = name + element['value']
                # elif key == "expression":
                #     expression = element['expression']

        return name

    @staticmethod
    def get_attributes(attributes_dict):
        attributes = list()
        if attributes_dict:
            for attribute_dict in attributes_dict:
                attribute = Element.from_dict(attribute_dict)
                if attribute:
                    attributes.append(attribute)
        return attributes

    @staticmethod
    def get_comment(comment_dict):
        comment = None
        if comment_dict:
            if "content" in comment_dict.keys():
                comment = comment_dict["content"]
        return comment

    @staticmethod
    def extract_elements_in_fluent(elements_in_fluent):
        """
        deal with elements in fluent syntax
        @param elements_in_fluent:
        @type elements_in_fluent:
        @return:
        @rtype:
        """
        if elements_in_fluent:
            for element_in_fluent in elements_in_fluent:
                if "value" in element_in_fluent.keys():
                    pass

    @staticmethod
    def extract_expression(expression_dict):
        pass

    @staticmethod
    def extract_selector(selector_dict):
        pass

    @staticmethod
    def extract_callee(callee_dict):
        pass

    # def get_category_from_html(self, tag):
    #     """
    #     get the category of element from html
    #
    #     @param tag:
    #     @type tag:
    #     @return:
    #     @rtype:
    #     """
    #     category = "Others"
    #     tag_tokens = []
    #     if self.id:
    #         tag_tokens.extend(NLPUtil.preprocess(self.id))
    #     if tag:
    #         if tag.name:
    #             tag_tokens.extend(NLPUtil.preprocess(tag.name))
    #         if tag.attrs:
    #             for value in tag.attrs.values():
    #                 if value and type(value) is list:
    #                     for one in value:
    #                         tag_tokens.extend(NLPUtil.preprocess(one))
    #                 elif type(value) is str:
    #                     tag_tokens.extend(NLPUtil.preprocess(value))
    #         if tag.parent.name:
    #             tag_tokens.extend(NLPUtil.preprocess(tag.parent.name))
    #         if tag.parent.parent.name:
    #             tag_tokens.extend(NLPUtil.preprocess(tag.parent.parent.name))
    #     for possible_category, tag in Placeholder.CATEGORY_TAG_DICT.items():
    #         if set(tag) & set(tag_tokens):
    #             category = possible_category
    #             break
    #     self.category = category
    #     # print(element)
    #     # print(tag.name)
    #     # print(tag.attrs)
    #     # print(tag.parent.name)
    #     # print(tag.parent.parent.name)
    #     # print(tag_tokens)
    #     # return

    @staticmethod
    def get_category_from_html(tag):
        """
        get the category of element from the tag in html
        @param tag: tag which has 'data-l10n-id' attribute
        @type tag: tag from html (beautiful soup parser)
        @return: category
        @rtype: string
        """
        category = "Others"
        tag_tokens = []
        if tag['data-l10n-id']:
            tag_tokens.extend(NLPUtil.preprocess(tag['data-l10n-id']))
            if tag.name:
                tag_tokens.extend(NLPUtil.preprocess(tag.name))
            if tag.attrs:
                for value in tag.attrs.values():
                    if value and type(value) is list:
                        for one in value:
                            tag_tokens.extend(NLPUtil.preprocess(one))
                    elif type(value) is str:
                        tag_tokens.extend(NLPUtil.preprocess(value))
            if tag.parent:
                # if tag.parent.name:
                tag_tokens.extend(NLPUtil.preprocess(tag.parent.name))
            if tag.parent.parent:
                # if tag.parent.parent.name:
                tag_tokens.extend(NLPUtil.preprocess(tag.parent.parent.name))
        for possible_category, tag in Placeholder.CATEGORY_TAG_DICT.items():
            if set(tag) & set(tag_tokens):
                category = possible_category
                break
        return category

    @staticmethod
    def get_category_from_data_l10n_id(data_l10n_id):
        """
        get the category of element from data-l10n-id in ftl
        @param data_l10n_id: 'data-l10n-id' attribute in ftl
        @type data_l10n_id: string
        @return: category
        @rtype: string
        """
        category = "Others"
        data_l10_id_tokens = []
        if data_l10n_id:
            data_l10_id_tokens.extend(NLPUtil.preprocess(data_l10n_id))
        for possible_category, tag in Placeholder.CATEGORY_TAG_DICT.items():
            if set(tag) & set(data_l10_id_tokens):
                category = possible_category
                break
        return category

    @staticmethod
    def get_elements_from_ftl_files(ftl_file_directory):
        """
        get elements from ftl files in ftl_file_directory
        @param ftl_file_directory: the filepath of ftl_file_directory
        @type ftl_file_directory: Path
        @return: elements
        @rtype: [Element, Element, Element, ... ,Element]
        """
        elements = []
        ftl_json_files = FileUtil.get_file_names_in_directory(ftl_file_directory, "json")
        for ftl_json_file in tqdm(ftl_json_files):
            ftl_dict = FileUtil.load_json(ftl_json_file)
            # logging.warning("Extract Elements from ftl...")
            if "body" in ftl_dict.keys():
                element_dict_list = ftl_dict["body"]
                # get elements
                for element_dict in element_dict_list:
                    element = Element.from_dict(element_dict)
                    if element:
                        elements.append(element)
        return elements

    @staticmethod
    def get_element_id_category_dict_from_html_files(html_file_directory):
        """
        get element_id_category_dict from (x)html files
        @param html_file_directory:
        @type html_file_directory: Path
        @return: element_id_category_dict
        @rtype: dict key: tag['data-l10n-id'] (string)
                     value: category (string)
        """
        element_id_tag_dict = dict()
        html_files = FileUtil.get_file_names_in_directory(html_file_directory, "*html")

        for html_file in tqdm(html_files):
            # print(html_file)
            with open(html_file, 'r') as result_page:
                soup = BeautifulSoup(result_page, 'html.parser')
            tags = soup.findAll(attrs={'data-l10n-id': re.compile(".+")})
            for tag in tags:
                element_id = tag['data-l10n-id']
                category = Element.get_category_from_html(tag)
                element_id_tag_dict[element_id] = element_id_tag_dict.get(element_id, set())
                element_id_tag_dict[element_id].add(category)
        return element_id_tag_dict

    @staticmethod
    def get_category_element_dict(ftl_file_directory, html_file_directory):
        """
        get category_element_dict (key: category (string), value: element (string))
        for elements in html: add categories into elements by html + data-l10n-id
        for elements not in html (maybe js): add categories into elements by data-l10n-id
        @param ftl_file_directory:
        @type ftl_file_directory:
        @param html_file_directory:
        @type html_file_directory:
        @return: dict
        @rtype: category_element_dict (key: category (string), value: element (string))
        """
        # get elements ([Element, Element, ...]) from ftl files
        logging.warning("get elements from ftl files")
        elements = Element.get_elements_from_ftl_files(ftl_file_directory)
        # for element in elements:
        #     print(element)

        # print("******************************************************************")
        logging.warning("get categories from html files")
        # get element_id_categories_dict (key: element_id (string), value: categories (set(string, string, ...))) from html files
        element_id_categories_dict = Element.get_element_id_category_dict_from_html_files(html_file_directory)
        # some element are not in html, in .js instead
        # for element_id, category in element_id_categories_dict.items():
        #     print(f"{element_id}: {category}")
        # print("******************************************************************")

        # add categories into elements
        # get category_element_dict (key: category (string), value: element (string))
        logging.warning("If category is not Others, add categories into elements by html + get category_element_dict")
        category_element_dict = dict()
        for element in tqdm(elements, ascii=True):
            # add categories into elements
            if element.id in element_id_categories_dict.keys():
                element.category = element_id_categories_dict[element.id]
                if element.category:
                    for category in element.category:
                        # if element.category != "Others":
                        category_element_dict[category] = category_element_dict.get(category, [])
                        # if want to get category_element_dict -> element is only string, please use the following two lines
                        element_strings = element.convert_element_to_string()
                        category_element_dict[category].extend(element_strings)
                        # only obtain same name elements
                        category_element_dict[category] = list(set(category_element_dict[category]))

                # if want to get category_element_dict -> element is Element, please use the following one line
                # category_element_dict[element.category].append(element)
        # for elements not in html (maybe in js)
        logging.warning("For elements not in html: "
                        # "if category is not Others, "
                        "add categories into elements by data_l10n_id only + "
                        "add into category_element_dict")
        for element in tqdm(elements, ascii=True):
            if element.category is None:
                # logging.warning(f"{element}")
                element.category = element.get_category_from_data_l10n_id(element.id)
                # if element.category != "Others":
                category_element_dict[element.category] = category_element_dict.get(element.category, [])
                # if want to get category_element_dict -> element is only string, please use the following two lines
                element_strings = element.convert_element_to_string()
                category_element_dict[element.category].extend(element_strings)
                # only obtain same name elements
                category_element_dict[element.category] = list(set(category_element_dict[element.category]))

        return category_element_dict

    # @staticmethod
    # def get_category_element_dict(component, ftl_filename, html_filename, product="firefox"):
    #     """
    #
    #     @param component:
    #     @type component:
    #     @param ftl_filename:
    #     @type ftl_filename:
    #     @param html_filename:
    #     @type html_filename:
    #     @param product:
    #     @type product:
    #     @return:
    #     @rtype:
    #     """
    #     filepath = Path(OUTPUT_DIR, f"{product}_gui", component, ftl_filename)
    #
    #     ftl_dict = FileUtil.load_json(filepath)
    #
    #     elements = []
    #     # logging.warning("Extract Elements from ftl...")
    #     if "body" in ftl_dict.keys():
    #         element_dict_list = ftl_dict["body"]
    #         # get elements
    #         for element_dict in element_dict_list:
    #             element = Element.from_dict(element_dict)
    #             if element:
    #                 elements.append(element)
    #     name_count = 0
    #     for element in elements:
    #         if element.name:
    #             name_count = name_count + 1
    #
    #     # print("******************************************************************")
    #
    #     # print(about_logins_ftl)
    #     # extract category from html
    #     filepath = Path(DATA_DIR, "firefox_gui", component, html_filename)
    #     with open(filepath, 'r') as result_page:
    #         soup = BeautifulSoup(result_page, 'html.parser')
    #     # count = 0
    #     tags = dict()
    #     for element in tqdm(elements):
    #         # tags = soup.findAll(attrs={"data-l10n-id": element.id})
    #         tag = soup.find(attrs={"data-l10n-id": element.id})
    #         element.get_cagegory_from_html(tag)
    #         # print("*************************************************")
    #         # print(element)
    #         # print(tag)
    #         if tag:
    #             tags[tag.name] = tags.get(tag.name, 0) + 1
    #             # element.category = tag.name
    #             # count = count + 1
    #     #         print(element)
    #     #         print(tag.name)
    #     #         # print(type(tag.name))
    #     #         print(tag.parent.name)
    #     #         # print(type(tag.parent.name))
    #     #         print(tag.parent.parent.name)
    #     #         # print(type(tag.parent.parent.name))
    #     #         print(tag.attrs)
    #     #         # print(type(tag.attrs))
    #     #         # print(tag.parent.parent.name)
    #     # print(count)
    #     # else:
    #     #     print(element)
    #     # print(element)
    #     # print(tag.name)
    #
    #     # input()
    #     # print("******************************************************************")
    #     # for key in tags.keys():
    #     #     print(f"{key}: {tags[key]}")
    #     category_element_dict = dict()
    #     for element in elements:
    #         category_element_dict[element.category] = category_element_dict.get(element.category, [])
    #         # if want to get category_element_dict -> element is only string, please use the following two lines
    #         element_strings = element.convert_element_to_string()
    #         category_element_dict[element.category].extend(element_strings)
    #         # only obtain same name elements
    #         category_element_dict[element.category] = list(set(category_element_dict[element.category]))
    #         # if want to get category_element_dict -> element is Element, please use the following one line
    #         # category_element_dict[element.category].append(element)
    #
    #     return category_element_dict

    def convert_element_to_string(self):
        """
        convert Element_object to string_list
        @return: string_list
        @rtype: list
        """
        element_strings = list()
        if self.name:
            element_strings.append(self.name)
        elif self.names_from_attributes:
            element_strings.extend(self.names_from_attributes)

        # filter element by special_chars = {'<', '>'} since if both have '<', '>', it maybe contain things, like<a></a>
        special_chars = {'<', '>'}
        filtered_element_str = []
        for element_string in element_strings:
            if special_chars.intersection(element_string) != special_chars:
                filtered_element_str.append(element_string)
        element_strings = filtered_element_str
        return element_strings

