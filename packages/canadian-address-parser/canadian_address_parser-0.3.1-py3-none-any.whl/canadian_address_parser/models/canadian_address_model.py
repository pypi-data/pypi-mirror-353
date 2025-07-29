import json
import re
from keyword import kwlist

import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoConfig
from peft import AutoPeftModelForSeq2SeqLM
import transformers

from ..errors.model_not_loaded import ModelNotLoaded
from ..errors.model_already_loaded import ModelAlreadyLoaded


class AddressParserModel:
    def __init__(self, hf_model_path: str, hf_token: str, max_output_length: int=300):
        self.__model_path = hf_model_path
        self.__hf_token = hf_token
        self.__max_output_length = max_output_length
        self.__tokenizer = None
        self.__model = None

    def __create_model_kwargs__(self) -> dict[str, str | bool]:
        model_args: dict[str, str | bool] = {
            'torch_dtype': torch.bfloat16,
            'token': self.__hf_token
        }
        if torch.cuda.is_available():
            model_args['load_in_4bit'] = True

        return model_args

    def load(self):
        transformers.logging.set_verbosity_error()

        if self.__tokenizer is not None or self.__model is not None:
            raise ModelAlreadyLoaded

        self.__tokenizer = AutoTokenizer.from_pretrained(self.__model_path, token=self.__hf_token)
        self.__model = AutoPeftModelForSeq2SeqLM.from_pretrained(self.__model_path, **self.__create_model_kwargs__())

    @staticmethod
    def __create_prompt__(raw_address_text: str) -> str:
        task = 'Extract address line, city, province code, and postal code from the messy Canadian address below and output a JSON with keys "address_line", "city", and "province_code", and "postal_code"'
        return f'{task}:\n{raw_address_text.upper()}'

    @staticmethod
    def __parse_response__(response: str) -> str:
        fix_quotes = lambda x: re.sub(r"[\'\"]+", '\'', x)
        remove_quotes = lambda x: re.sub(r"[\'\"]+", '', x)

        response = re.sub(r'([\'\"]#[0-9]+)[\'\"](, )[\'\"]', r'\1\2', response)
        kv_pairs = re.sub('\', ', '\',', fix_quotes(response.strip())).split('\',')
        parsed_kv_pairs = [(f'{remove_quotes(k.strip())}', f'{fix_quotes(v.strip())}') for k, v in [x.split(': ') for x in kv_pairs]]

        res = {}
        for k, v in parsed_kv_pairs:
            res[remove_quotes(k)] = remove_quotes(v)

        return json.dumps(res)


    def parse_address(self, raw_address_text: str) -> str:
        if self.__tokenizer is None or self.__model is None:
            raise ModelNotLoaded

        pipe = pipeline('text2text-generation', model=self.__model, tokenizer=self.__tokenizer,
                        max_length=self.__max_output_length)
        prompt = self.__create_prompt__(raw_address_text.upper())
        raw_output = pipe(prompt)[0]['generated_text']

        return self.__parse_response__(raw_output)