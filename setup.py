from setuptools import find_packages, setup 

setup(
    name="MCQ_Generator",
    version="0.0.1",
    author="Dhruv Pamneja",
    author_email="dpamneja@gmail.com",
    install_requires = ["openai","langchain","streamlit","python-dotenv","PyPDF"],
    packages=find_packages()
)