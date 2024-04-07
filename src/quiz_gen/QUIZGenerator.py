# Importing the dependencies and loading the environment variables
import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.quiz_gen.utils import read_file, get_table_data
from src.quiz_gen.logger import logging

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

load_dotenv()
KEY = os.getenv("OPENAI_API_KEY")

# Initialising the client

llm = ChatOpenAI(openai_api_key = KEY, model_name = "gpt-3.5-turbo",temperature = 0.3)
logging.info("Client Initialised")

# Initialising the templates and the prompts
template_mcq = """
Text: {text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz of {number_mcq} multiple choice questions for {subject} students in {tone} tone.
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like RESPONSE_MCQ_JSON below and use it as a guide. Make sure to just give the json as it is in 
the below given format\
Ensure to make {number_mcq} MCQs 

{response_MCQ_json}
"""

template_tfq = """
Text: {text}
You are an expert True False Question maker. Given the above text, it is your job to \
create a quiz of {number_tfq} True/False questions for {subject} students in {tone} tone.
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like RESPONSE_TFQ_JSON below and use it as a guide. Make sure to just give the json as it is in 
the below given format\
Ensure to make {number_tfq} TFQs

{response_TFQ_json}
"""

quiz_gen_MCQ_prompt = PromptTemplate(
    input_variables=["text","number_mcq","subject","tone","response_MCQ_json"],
    template=template_mcq
)

quiz_gen_TFQ_prompt = PromptTemplate(
    input_variables=["text","number_tfq","subject","tone","response_TFQ_json"],
    template=template_tfq
)

logging.info("Templates and Prompts Initialised")

# Initialising the LLM Chain(s) to connect client and prompt

quiz_gen_MCQ_chain = LLMChain(llm=llm, prompt = quiz_gen_MCQ_prompt, output_key = "quiz_MCQ", verbose = True)
quiz_gen_TFQ_chain = LLMChain(llm=llm, prompt = quiz_gen_TFQ_prompt, output_key = "quiz_TFQ", verbose = True)

logging.info("Chains Initialised")

# Setting the Ouput Prompts

output_template_mcq = """
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz_MCQ}

Check from an expert English Writer of the above quiz:
"""

output_template_tfq = """
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz_TFQ}

Check from an expert English Writer of the above quiz:
"""

logging.info("Output Prompts Initialised")

# Initialising the Review Prompts and Chains

quizEval_MCQ_prompt_template = PromptTemplate(input_variables=["subject","quiz_MCQ"],template=output_template_mcq)
review_MCQ_chain = LLMChain(llm=llm,prompt=quizEval_MCQ_prompt_template,output_key="review_MCQ",verbose=True)

quizEval_TFQ_prompt_template = PromptTemplate(input_variables=["subject","quiz_TFQ"],template=output_template_tfq)
review_TFQ_chain = LLMChain(llm=llm,prompt=quizEval_TFQ_prompt_template,output_key="review_TFQ",verbose=True)

logging.info("Review Prompts and Chains Initialised")

# Creating the Sequential Chains to combine the Input and Output Review Chains

evaluation_chain_MCQ = SequentialChain(
    chains=[quiz_gen_MCQ_chain,review_MCQ_chain],
    input_variables=["text","number_mcq","subject","tone","response_MCQ_json"],
    output_variables=["quiz_MCQ","review_MCQ"],
    verbose=True
)

evaluation_chain_TFQ = SequentialChain(
    chains=[quiz_gen_TFQ_chain,review_TFQ_chain],
    input_variables=["text","number_tfq","subject","tone","response_TFQ_json"],
    output_variables=["quiz_TFQ","review_TFQ"],
    verbose=True
)

logging.info("Sequential Chains Loaded")
logging.info("----------------------------------")













