import os
import PyPDF2
import json
import traceback
from src.quiz_gen.logger import logging

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfFileReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
                
            logging.info("Text Loaded via PDF")
            return text
        except:
            raise Exception("Error while reading the PDF file.")
        
    
    elif file.name.endswith(".txt"):
        logging.info("Text Loaded via Text File")
        return file.read().decode("utf-8")
    
    else:
        raise Exception("Only PDF/Text file supported.")
    
    
def get_table_data(quiz_mcq_str,quiz_tfq_str):
    try:
        quiz_mcq = json.loads(quiz_mcq_str)
        quiz_tfq = json.loads(quiz_tfq_str)
        
        logging.info("Quizzes loaded as JSONs")
        
        quiz_mcq_table_data = []
        for key, value in quiz_mcq.items():
            mcq = value["mcq"]
            options = " | ".join(
                [
                    f"{option}: {option_value}"
                    for option, option_value in value["options"].items()
                    ]
                )
            correct = value["correct"]
            quiz_mcq_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})
            
        if quiz_mcq_table_data is not None:
            logging.info("MCQ Quiz table loaded")
            
        quiz_tfq_table_data = []
        for key, value in quiz_tfq.items():
            tfq = value["tfq"]
            options = " | ".join(
                [
                    f"{option}: {option_value}"
                    for option, option_value in value["options"].items()
                    ]
                )
            correct = value["correct"]
            quiz_tfq_table_data.append({"TFQ": tfq, "Choices": options, "Correct": correct})
            
        if quiz_tfq_table_data is not None:
            logging.info("TFQ Quiz table loaded")
            
        logging.info("Quizes stored")
        return [quiz_mcq_table_data,quiz_tfq_table_data]
    except Exception as e:
        traceback.print_exception(type(e),e,e.__traceback__)
        return []
    
logging.info("----------------------------------")
        