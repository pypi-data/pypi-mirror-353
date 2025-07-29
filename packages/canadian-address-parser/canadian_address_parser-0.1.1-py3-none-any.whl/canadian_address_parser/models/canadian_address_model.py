from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
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

    def load(self):
        transformers.logging.set_verbosity_error()

        if self.__tokenizer is not None or self.__model is not None:
            raise ModelAlreadyLoaded

        self.__tokenizer = AutoTokenizer.from_pretrained(self.__model_path, token=self.__hf_token)
        self.__model = AutoModelForCausalLM.from_pretrained(self.__model_path,
                                                            torch_dtype='auto',
                                                            token=self.__hf_token,
                                                            load_in_4bit=True)

    @staticmethod
    def __create_prompt__(raw_address_text: str) -> str:
        return f'Raw Input: {raw_address_text.upper()}'

    @staticmethod
    def __parse_response__(response: str) -> str:
        output_start_token = '<OUTPUT>\nClean Address: '
        output_start = response.index(output_start_token) + len(output_start_token)
        output_end = response.index('\n</OUTPUT>')
        return response[output_start:output_end]

    def parse_address(self, raw_address_text: str) -> str:
        if self.__tokenizer is None or self.__model is None:
            raise ModelNotLoaded

        pipe = pipeline('text-generation', model=self.__model, tokenizer=self.__tokenizer,
                        max_length=self.__max_output_length)
        prompt = f'<INPUT>\n{self.__create_prompt__(raw_address_text)}\n</INPUT>\n'
        response = pipe(prompt)[0]['generated_text']
        return self.__parse_response__(response)