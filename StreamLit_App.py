# Importing the dependencies and loading the environment variables
import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
from src.quiz_gen.QUIZGenerator import evaluation_chain_MCQ, evaluation_chain_TFQ
from langchain.callbacks import get_openai_callback
from src.quiz_gen.utils import read_file, get_table_data
from src.quiz_gen.logger import logging


# Loading the JSON files

with open('./Response_MCQ.json') as file:
    response_MCQ_json = json.load(file)

with open('./Response_TFQ.json') as file:
    response_TFQ_json = json.load(file)
    
    
# Title 
st.title("Quiz Generator Application using Langchain")

# User Input
with st.form("user_inputs"):
    # File Upload
    uploaded_file = st.file_uploader("Upload a PDF/Text File")
    
    # Input Fields 
    question_count = st.number_input("Enter the number of questions", min_value=3,max_value=20)
    mcq_count = question_count//2
    tfq_count = question_count - mcq_count
    
    # Subject 
    subject = st.text_input("Insert Subejct")
    
    # Complexity 
    tone_list = ["Easy","Medium","Hard"]
    tone = st.selectbox("Complexity of the Questions", tone_list)
    
    # Submission Button
    button = st.form_submit_button("Create Quiz")
    
    # Check to ensure values are submitted
    
    if button and uploaded_file is not None and mcq_count and subject and tone:
        logging.info("Final user input received for Quiz")
        with st.spinner("Loading..."):
            try:
                text_mcq = read_file(uploaded_file)
                # Getting the cost of API Call and Number of Tokens
                with get_openai_callback() as cb:
                    response_MCQ = evaluation_chain_MCQ({
                                    "text": text_mcq,
                                    "number_mcq": mcq_count,
                                    "subject":subject,
                                    "tone": tone,
                                    "response_MCQ_json": json.dumps(response_MCQ_json)
                                }
                    )
                logging.info("MCQ Quiz Generated")
                logging.info(f"Total Tokens:{cb.total_tokens}")
                logging.info(f"Prompt Tokens:{cb.prompt_tokens}")
                logging.info(f"Completion Tokens:{cb.completion_tokens}")
                logging.info(f"Total Cost in USD:{cb.total_cost}")
                
                text_tfq = read_file(uploaded_file)
                with get_openai_callback() as cb2:
                    response_TFQ = evaluation_chain_TFQ({
                                    "text": text_tfq,
                                    "number_tfq": tfq_count,
                                    "subject":subject,
                                    "tone": tone,
                                    "response_TFQ_json": json.dumps(response_TFQ_json)
                                }
                    )
                logging.info("TFQ Quiz Generated")
                logging.info(f"Total Tokens:{cb2.total_tokens}")
                logging.info(f"Prompt Tokens:{cb2.prompt_tokens}")
                logging.info(f"Completion Tokens:{cb2.completion_tokens}")
                logging.info(f"Total Cost in USD:{cb2.total_cost}")
                
                
            except Exception as e:
                traceback.print_exception(type(e),e,e.__traceback__)
                st.error("Error")
                
            else:        
                if isinstance(response_MCQ,dict) and isinstance(response_TFQ,dict):
                    quiz_mcq = response_MCQ.get('quiz_MCQ',None)     
                    quiz_tfq = response_TFQ.get('quiz_TFQ',None)    
                    
                    if quiz_tfq is not None and quiz_mcq is not None:
                        quizzes = get_table_data(quiz_mcq,quiz_tfq)
                        table_MCQ_data = quizzes[0]
                        table_TFQ_data = quizzes[1]
                        if table_MCQ_data is not None and table_TFQ_data is not None:
                            df_mcq = pd.DataFrame(table_MCQ_data)
                            df_tfq = pd.DataFrame(table_TFQ_data)
                            
                            df_mcq.index = df_mcq.index+1
                            df_tfq.index = df_tfq.index+1
                            
                            st.table(df_mcq)
                            st.text_area(label="Review_MCQ",value=response_MCQ["review_MCQ"])
                            
                            
                            st.table(df_tfq)
                            st.text_area(label="Review_TFQ",value=response_TFQ["review_TFQ"])
                            logging.info("----------------------------------")
                        else:
                            st.error("Error in the table data")
                else:
                    st.write(response_MCQ)
                    st.write(response_TFQ)
                    
                        
                        
                        
                        
                    
                        
                    
        
    
    