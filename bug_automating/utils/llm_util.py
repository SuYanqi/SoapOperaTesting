import copy
import json
import os
import time

import openai
# import time
import backoff
from openai import OpenAI

from bug_automating.pipelines.placeholder import Placeholder
from bug_automating.utils.file_util import FileUtil


class LLMUtil:
    OPENAI_API_KEY = "sk-proj-48MJRpOF8Z5pJMjLknGDT3BlbkFJabKkgTSUVUMLEgTmBMEt"
    NO_KNOWLEDGE_BASE_ASSISTANT_ID = "asst_H3veqzbHkGhrmwjuh4ROkb42"
    NO_KNOWLEDGE_BASE_VECTOR_STORE_ID = "vs_ZbQL6MIdSh8CraHiYiXqqVa5"
    FENIX_TEST_SCENARIO_VECTOR_STORE_ID = "vs_3XSIno2IO2tqqa5ZKb86wDKk"
    FENIX_STEP_CLUSTER_VECTOR_STORE_ID = None
    FENIX_PLANNER_ASSISTANT_ID = "asst_7Egfx1xos1NMkRa1pGNpRSzN"
    FENIX_CLUSTER_IDENTIFIER_ASSISTANT_ID = "asst_WKDsS5XtJqvjaZBRRUnH3jL7"
    FENIX_PLANNER_THREAD_ID = None

    ANTENNAPOD_TEST_SCENARIO_VECTOR_STORE_ID = "vs_qSbWGlIWJBZM5tI9tTh3DY22"
    ANTENNAPOD_PLANNER_ASSISTANT_ID = "asst_0CCvQBth0Hrf86RjVppbkJmx"
    ANTENNAPOD_CLUSTER_IDENTIFIER_ASSISTANT_ID = "asst_ZomMtQgeIxRFZqbSzA2OCIhz"

    WORDPRESS_TEST_SCENARIO_VECTOR_STORE_ID = "vs_71khghXen4a1SmKjneFmaS6y"
    WORDPRESS_PLANNER_ASSISTANT_ID = "asst_KFXIFNF0GQXG7pQekw9it4LJ"
    WORDPRESS_CLUSTER_IDENTIFIER_ASSISTANT_ID = "asst_54ZgvRRfCvV0LVZfkDa2X7Jb"


    client = OpenAI(api_key=OPENAI_API_KEY)
    GPT3_5_MODEL_NAME = "gpt-3.5-turbo-1106"
    GPT4_MODEL_NAME = "gpt-4"
    GPT4_TURBO_MODEL_NAME = "gpt-4-turbo"
    GPT4O_MODEL_NAME = "gpt-4o"
    GPT4O_MODEL_NAME_WITH_DATE_05 = "gpt-4o-2024-05-13"
    GPT4O_MODEL_NAME_WITH_DATE_08 = "gpt-4o-2024-08-06"
    GPT4O_MINI_NAME = "gpt-4o-mini"
    GPT4O_MINI_NAME_WITH_DATE = "gpt-4o-mini-2024-07-18"
    GPT4_PREVIEW_MODEL_NAME = "gpt-4-1106-preview"
    GPT3_5_TURBO_0125_MODEL_NAME = "gpt-3.5-turbo-0125"

    GPT4O_05_PRICE_PER_PROMPT_TOKEN = 5.0 / 1_000_000  # $5 per 1M prompt tokens (input)
    GPT4O_05_PRICE_PER_COMPLETION_TOKEN = 15.0 / 1_000_000  # $15 per 1M completion tokens (output)

    GPT4O_08_PRICE_PER_PROMPT_TOKEN = 2.5/1_000_000  # $5 per 1M prompt tokens (input)
    GPT4O_08_PRICE_PER_COMPLETION_TOKEN = 10.0/1_000_000  # $15 per 1M completion tokens (output)

    GPT4O_MINI_PRICE_PER_PROMPT_TOKEN = 0.15/1_000_000  # $0.15 per 1M prompt tokens (input)
    GPT4O_MINI_PRICE_PER_COMPLETION_TOKEN = 0.6/1_000_000  # $0.6 per 1M completion tokens (output)

    TEXT_EMBEDDING_MODEL_NAME = "text-embedding-3-large"

    ROLE_SYSTEM = 'system'
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    SESSION_PROMPT = ""
    CHAT_LOG = None
    # CHAIN_OF_THOUGHTS = 'CHAIN_OF_THOUGHTS'

    TEXT_INPUT = """
    {{
        "type": "text",
        "text": {text_value}
    }}
    """

    IMAGE_BASE64_INPUT = """
    {{
        "type": "image_url",
        "image_url": {{
            "url": "data:image/png;base64,{base64_image}",
            "detail": "{img_detail}"
        }}
    }}
    """

    QUESTION_WITH_IMAGE_BASE64 = """
[
    {{
        "type": "text",
        "text": {text_value}
    }},
    {{
        "type": "image_url",
        "image_url": {{
            "url": "data:image/png;base64,{base64_image}",
            "detail": "{img_detail}"
        }}
    }}
]
"""

    QUESTION_WITH_2_IMAGE_BASE64 = """
    [
        {{
            "type": "text",
            "text": 
                {text_value}
        }},
        {{
            "type": "image_url",
            "image_url": {{
                "url": "data:image/png;base64,{base64_image}",
                "detail": "{img_detail}"
            }}
        }},
        {{
            "type": "image_url",
            "image_url": {{
                "url": "data:image/png;base64,{base64_image1}",
                "detail": "{img_detail}"
            }}
        }}
    ]
    """

    @staticmethod
    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    def ask_llm_for_chat_completions(messages, model=GPT4O_MODEL_NAME, temperature=1):
        """
        ask LLM question
        Args:
            temperature (): number Optional Defaults to 1
                            What sampling temperature to use, between 0 and 2.
                            Higher values like 0.8 will make the output more random,
                            while lower values like 0.2 will make it more focused and deterministic.
                            We generally recommend altering this or top_p but not both.
            model ():
            messages ():

        Returns: answer

        """
        response = LLMUtil.client.chat.completions.create(
            model=model,
            # seed=1,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        total_cost = LLMUtil.calculate_costs(response)
        answer = response.choices[0].message.content
        return answer, total_cost

    @staticmethod
    def add_cost_into_answer(answer, total_cost):
        answer_copy = copy.deepcopy(answer)
        answer_copy[Placeholder.COST] = total_cost
        return answer_copy

    @staticmethod
    @backoff.on_exception(backoff.expo, openai.RateLimitError)
    def ask_llm_for_embedding(texts, model=TEXT_EMBEDDING_MODEL_NAME):
        """
        # Example texts
        input: texts = ["example text 1", "example text 2"]
        return embeddings = [embedding1, embedding2]
        """
        # response = LLMUtil.client.embeddings.create(
        #     input=[text],
        #     model=model
        # )
        response = LLMUtil.client.embeddings.create(input=texts, model=model).data
        embeddings = []
        for one_embedding in response:
            embeddings.append(one_embedding.embedding)
        return embeddings

    @staticmethod
    def get_messages(session_prompt, qa_pairs=None):
        """
        model="gpt-3.5-turbo",
        Args:
            system_role: for session_prompt,
            question_role: for question,
            answer_role: for answer,
            session_prompt: for system_role introduction
            qa_pairs (examples): (Q, A) pairs

        Returns:
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
                {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                {"role": "user", "content": "Where was it played?"}
            ]
        """
        messages = [{'role': LLMUtil.ROLE_SYSTEM, 'content': session_prompt}]
        if qa_pairs:
            for qa in qa_pairs:
                role_content_dict = {'role': LLMUtil.ROLE_USER, 'content': qa[0]}
                messages.append(role_content_dict)
                role_content_dict = {'role': LLMUtil.ROLE_ASSISTANT, 'content': qa[1]}
                messages.append(role_content_dict)
        return messages

    @staticmethod
    def add_role_content_dict_into_messages(role, content, messages):
        role_content_dict = {'role': role, 'content': content}
        messages.append(role_content_dict)
        return messages

    @staticmethod
    def show_messages(messages):
        for message in messages:
            if isinstance(message['content'], dict):
                pass
            else:
                print(f"{message['role']}: {message['content']}")

    @staticmethod
    def get_messages_without_image_encode(messages):
        for message in messages:
            if message['role'] == LLMUtil.ROLE_USER:
                question = message['content']
                message['content'] = LLMUtil.get_question_without_image_encode(question)
        return messages

    @staticmethod
    def get_question_without_image_encode(question):
        for one_dict in question:
            if one_dict['type'] == "image_url":
                one_dict["image_url"]["url"] = None
        return question

    @staticmethod
    def calculate_tokens(messages):
        question = ''
        answer = ''
        system = ''
        for message in messages:
            if message['role'] == LLMUtil.ROLE_USER:
                question = message['content']
            elif message['role'] == LLMUtil.ROLE_ASSISTANT:
                answer = message['content']
            elif message["role"] == LLMUtil.ROLE_SYSTEM:
                system = message['content']
        question = system + question
        # print("#######test##########")
        # print(question)
        # print(answer)
        # print("#######test##########")
        question_tokens = question.split()
        answer_tokens = answer.split()
        print(f"###len(que_tokens): {len(question_tokens)} len(ans_tokens): {len(answer_tokens)}###")
        return len(question_tokens), len(answer_tokens)

    # *******************************************Assistant***********************************************
    @staticmethod
    def create_assistant(assistant_name,
                         instructions,
                         vector_store_id=None,
                         vector_store_name=None,
                         filepath=None,
                         model_name=GPT4O_MODEL_NAME,
                         temperature=0.2):
        if vector_store_id:
            vector_store = LLMUtil.retrieve_vector_store_by_id(vector_store_id=vector_store_id)
        else:
            vector_store = LLMUtil.create_vector_store(vector_store_name, filepath)
        assistant = LLMUtil.client.beta.assistants.create(
            name=assistant_name,
            instructions=instructions,
            model=model_name,
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
            temperature=temperature,
            response_format="auto"  # {"type": "json_object"}
        )
        # return assistant
        print(f"!!!assistant id is {assistant.id} !!!")
        return assistant, vector_store

    @staticmethod
    def create_vector_store(vector_store_name, filepath):
        # Upload the user provided file to OpenAI
        message_file = LLMUtil.client.files.create(
            file=open(str(filepath), "rb"), purpose="assistants"
        )
        vector_store = LLMUtil.client.beta.vector_stores.create(name=vector_store_name,
                                                                file_ids=[message_file.id])
        print(vector_store.id)
        print(vector_store)
        # Check the status of vector store creation
        while vector_store.status == 'in_progress':
            vector_store = LLMUtil.client.beta.vector_stores.retrieve(vector_store_id=vector_store.id)
            print(vector_store.id)
            # status = response['status']
            print(f"Current status: {vector_store.status}")
            time.sleep(5)  # Wait for 5 seconds before checking again
        return vector_store

    @staticmethod
    def retrieve_vector_store_by_id(vector_store_id):
        if vector_store_id is None:
            return None
        return LLMUtil.client.beta.vector_stores.retrieve(vector_store_id=vector_store_id)

    @staticmethod
    def retrieve_assistant_by_id(assistant_id):
        return LLMUtil.client.beta.assistants.retrieve(assistant_id=assistant_id)

    @staticmethod
    def create_thread(messages=None):
        # Create a thread and attach the file to the message
        if messages:
            thread = LLMUtil.client.beta.threads.create(
                messages=messages
            )
        else:
            thread = LLMUtil.client.beta.threads.create()
        print(f"!!!thread id is {thread.id} !!!")
        return thread

    @staticmethod
    def retrieve_thread_by_id(thread_id):
        return LLMUtil.client.beta.threads.retrieve(thread_id=thread_id)

    @staticmethod
    def get_assistant_messages(question, with_img_filepath=None, with_instances=True):
        # @todo two instances
        messages = [
            {
                "role": "user",
                "content": question,
            }
        ]
        if with_img_filepath:
            file = LLMUtil.client.files.create(
                file=open(with_img_filepath, "rb"),
                purpose="vision"
            )
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        # {
                        #     "type": "image_url",
                        #     "image_url": {"url": "https://example.com/image.png"}
                        #     "detail": "high"

                        # },
                        {
                            "type": "image_file",
                            "image_file": {"file_id": file.id},
                        },
                    ],
                },
            ]
        return messages

    @staticmethod
    def get_thread_messages(thread_id, question, with_img_filepath=None, with_original_img_filepath=None,
                            with_instances=False):
        # @todo two instances
        messages_content = [
            {
                "type": "text",
                "text": question
            },
        ]
        img_filepath_list = [with_img_filepath, with_original_img_filepath]
        for img_filepath in img_filepath_list:
            if img_filepath:
                file = LLMUtil.client.files.create(
                    file=open(img_filepath, "rb"),
                    purpose="vision"
                )
                file_content = {
                    "type": "image_file",
                    "image_file": {"file_id": file.id},
                }
                messages_content.append(file_content)

        thread_messages = LLMUtil.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=messages_content)
        return thread_messages

    @staticmethod
    def show_thread_messages(thread_id):
        thread_messages = LLMUtil.client.beta.threads.messages.list(thread_id=thread_id)
        sorted_messages = sorted(thread_messages.data, key=lambda x: x.created_at)
        for msg in sorted_messages:
            if msg.role == "assistant":
                print("Assistant:", msg.content[0].text.value)
            else:
                print("User:", msg.content[0].text.value)
###################################################################################################################
    # @staticmethod
    # def calculate_chat_completions_costs(response):
    #     model_name = response.model
    #     prompt_tokens = response.usage.prompt_tokens
    #     completion_tokens = response.usage.completion_tokens
    #     total_cost = LLMUtil.calculate_costs(model_name, prompt_tokens, completion_tokens)
    #     return total_cost

    # @staticmethod
    # def calculate_assistant_costs(run_id):
    #     run = LLMUtil.client.beta.runs.retrieve(run_id=run_id)
    #     usage = run_details['usage']
    #     prompt_tokens = usage['prompt_tokens']
    #     completion_tokens = usage['completion_tokens']
    #     total_cost = LLMUtil.calculate_costs(run.model, prompt_tokens, completion_tokens)
    #     return total_cost

    # @staticmethod
    # def get_tokens(response):
    #     model_name = response.model
    #     prompt_tokens = response.usage.prompt_tokens
    #     completion_tokens = response.usage.completion_tokens
    #     total_cost = LLMUtil.calculate_costs(model_name, prompt_tokens, completion_tokens)
    #     return total_cost

    @staticmethod
    def calculate_costs(response):
        model_name = response.model
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        if model_name in [LLMUtil.GPT4O_MODEL_NAME, LLMUtil.GPT4O_MODEL_NAME_WITH_DATE_05]:
            # Define pricing per million tokens
            price_per_prompt_token = LLMUtil.GPT4O_05_PRICE_PER_PROMPT_TOKEN
            price_per_completion_token = LLMUtil.GPT4O_05_PRICE_PER_COMPLETION_TOKEN
        elif model_name in [LLMUtil.GPT4O_MODEL_NAME_WITH_DATE_08]:
            # Define pricing per million tokens
            price_per_prompt_token = LLMUtil.GPT4O_08_PRICE_PER_PROMPT_TOKEN
            price_per_completion_token = LLMUtil.GPT4O_08_PRICE_PER_COMPLETION_TOKEN
        elif model_name in [LLMUtil.GPT4O_MINI_NAME, LLMUtil.GPT4O_MINI_NAME_WITH_DATE]:
            price_per_prompt_token = LLMUtil.GPT4O_MINI_PRICE_PER_PROMPT_TOKEN
            price_per_completion_token = LLMUtil.GPT4O_MINI_PRICE_PER_COMPLETION_TOKEN
        # Calculate cost for the prompt tokens
        prompt_cost = prompt_tokens * price_per_prompt_token
        # Calculate cost for the completion tokens
        completion_cost = completion_tokens * price_per_completion_token
        # Total cost
        total_cost = prompt_cost + completion_cost
        # print(f"Model: {model_name}\nprice_per_prompt_token: {price_per_prompt_token}\nprice_per_completion_token: {price_per_completion_token}\nInput tokens: {prompt_tokens}\nOutput tokens: {completion_tokens}\nTotal costs: {total_cost} USD")
        cost = {
            "model": model_name,
            "price_per_prompt_token": price_per_prompt_token,
            "price_per_completion_token": price_per_completion_token,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_cost": total_cost
        }
        return cost

