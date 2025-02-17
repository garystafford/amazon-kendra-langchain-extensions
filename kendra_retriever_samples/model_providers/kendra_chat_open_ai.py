import os

from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.retrievers import AmazonKendraRetriever

# ***** CONFIGURABLE PARAMETERS *****
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-3.5-turbo")
TEMPERATURE = os.environ.get("TEMPERATURE", 1e-10)
MAX_TOKENS = os.environ.get("MAX_TOKENS", 1024)  # Maximum number of tokens to generate
TOP_K = os.environ.get("TOP_K", 250)
TOP_P = os.environ.get("TOP_P", .5)
KENDRA_INDEX_ID = os.environ["KENDRA_INDEX_ID"]
MAX_HISTORY_LENGTH = 5
# ******************************************************************


def build_chain():
    llm = ChatOpenAI(temperature=TEMPERATURE, max_tokens=MAX_TOKENS, model=MODEL_NAME)

    retriever = AmazonKendraRetriever(index_id=KENDRA_INDEX_ID)

    prompt_template = """
  The following is a friendly conversation between a human and an AI. 
  The AI is talkative and provides lots of specific details from its context.
  If the AI does not know the answer to a question, it truthfully says it 
  does not know.
  {context}
  Instruction: Based on the above documents, provide a detailed answer for, {question} Answer "don't know" 
  if not present in the document. 
  Solution:"""
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    condense_qa_template = """
  Given the following conversation and a follow up question, rephrase the follow up question 
  to be a standalone question.

  Chat History:
  {chat_history}
  Follow Up Input: {question}
  Standalone question:"""
    standalone_question_prompt = PromptTemplate.from_template(condense_qa_template)

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        condense_question_prompt=standalone_question_prompt,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt},
    )
    return qa


def run_chain(chain, prompt: str, history=None):
    if history is None:
        history = []
    return chain({"question": prompt, "chat_history": history})
