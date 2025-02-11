# Conversational Retrieval QA Chatbot, built using Langflow and Streamlit
# Author: Gary A. Stafford
# Date: 2023-08-19
# Requirements: pip install -r requirements.txt -U
# Usage: streamlit run app.py <flanxl|flanxxl|llama2chat|falcon|bedrockclaude|bedrocktitan|bedrockai21labs|openai|cohere> --server.runOnSave true

import os
import sys

import streamlit as st

from model_providers import (
    kendra_chat_bedrock_anthropic_claude as bedrockclaude,
    kendra_chat_bedrock_amazon_titan as bedrocktitan,
    kendra_chat_bedrock_ai21_labs as bedrockai21labs,
    kendra_chat_open_ai as openai,
    kendra_chat_flan_xxl as flanxxl,
    kendra_chat_flan_xl as flanxl,
    kendra_chat_llama2_chat as llama2chat,
    kendra_chat_falcon as falcon,
    kendra_chat_cohere as cohere,
)

# ****** CONFIGURABLE PARAMETERS ******
USER_ICON = os.environ.get("USER_ICON", "images/user-icon.png")
AI_ICON = os.environ.get("AI_ICON", "images/ai-icon.png")
HEADER_TITLE = os.environ.get("HEADER_TITLE", "A Chatbot powered by Amazon Kendra")
HEADER_LOGO = os.environ.get("HEADER_LOGO", "images/ai-icon.png")
PAGE_TITLE = os.environ.get("PAGE_TITLE", "AI Chatbot")
PAGE_FAVICON = os.environ.get("PAGE_FAVICON", "images/ai-icon.png")
SHOW_DOC_SOURCES = os.environ.get("SHOW_DOC_SOURCES", True)
TEXT_INPUT_PROMPT = os.environ.get(
    "TEXT_INPUT_PROMPT", "Ask me any question about Amazon SageMaker."
)
TEXT_INPUT_PLACEHOLDER = os.environ.get(
    "TEXT_INPUT_PLACEHOLDER", "What is Amazon SageMaker?"
)
TEXT_INPUT_HELP = os.environ.get(
    "TEXT_INPUT_HELP",
    "For more help, see our official documentation: https://docs.aws.amazon.com/sagemaker/index.html",
)
SHOW_SAMPLE_QUESTIONS = os.environ.get("SHOW_SAMPLE_QUESTIONS", True)
MAX_HISTORY_LENGTH = os.environ.get("MAX_HISTORY_LENGTH", 5)
PROVIDER_MAP = {
    "openai": os.environ.get("OPENAI_MODEL_NAME", "OpenAI GPT-3.5 Turbo"),
    "flanxl": os.environ.get("FLANXL_MODEL_NAME", "Flan-T5-XL"),
    "flanxxl": os.environ.get("FLANXXL_MODEL_NAME", "Flan-T5-XXL"),
    "llama2chat": os.environ.get("LLAMA_MODEL_NAME", "Llama-2 13B Chat"),
    "falcon": os.environ.get("FALCON_MODEL_NAME", "Falcon 40B BF16"),
    "bedrockclaude": os.environ.get(
        "BEDROCK_CLAUDE_MODEL_NAME", "Bedrock Anthropic Claude"
    ),
    "bedrocktitan": os.environ.get(
        "BEDROCK_TITAN_MODEL_NAME", "Titan Text Large"
    ),
    "bedrockai21labs": os.environ.get(
        "BEDROCK_AI21_LABS_MODEL_NAME", "AI21 Labs Jurassic-2"
    ),
    "cohere": os.environ.get(
        "COHERE_MODEL_NAME", "Cohere Command"
    ),
}


def main():
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_FAVICON,
    )

    if "llm_chain" not in st.session_state:
        if len(sys.argv) > 1:
            if sys.argv[1] == "flanxl":
                st.session_state["llm_app"] = flanxl
                st.session_state["llm_chain"] = flanxl.build_chain()
            elif sys.argv[1] == "flanxxl":
                st.session_state["llm_app"] = flanxxl
                st.session_state["llm_chain"] = flanxxl.build_chain()
            elif sys.argv[1] == "openai":
                st.session_state["llm_app"] = openai
                st.session_state["llm_chain"] = openai.build_chain()
            elif sys.argv[1] == "llama2chat":
                st.session_state["llm_app"] = llama2chat
                st.session_state["llm_chain"] = llama2chat.build_chain()
            elif sys.argv[1] == "falcon":
                st.session_state["llm_app"] = falcon
                st.session_state["llm_chain"] = falcon.build_chain()
            elif sys.argv[1] == "bedrockclaude":
                st.session_state["llm_app"] = bedrockclaude
                st.session_state["llm_chain"] = bedrockclaude.build_chain()
            elif sys.argv[1] == "bedrocktitan":
                st.session_state["llm_app"] = bedrocktitan
                st.session_state["llm_chain"] = bedrocktitan.build_chain()
            elif sys.argv[1] == "bedrockai21labs":
                st.session_state["llm_app"] = bedrockai21labs
                st.session_state["llm_chain"] = bedrockai21labs.build_chain()
            elif sys.argv[1] == "cohere":
                st.session_state["llm_app"] = cohere
                st.session_state["llm_chain"] = cohere.build_chain()
            else:
                raise Exception("Unsupported LLM: ", sys.argv[1])
        else:
            raise Exception(
                "Usage: streamlit run app.py <flanxl|flanxxl|llama2chat|falcon|bedrockclaude|bedrocktitan|bedrockai21labs|openai|cohere>"
            )

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    if "chats" not in st.session_state:
        st.session_state.chats = [{"id": 0, "question": "", "answer": ""}]

    if "questions" not in st.session_state:
        st.session_state.questions = []

    if "answers" not in st.session_state:
        st.session_state.answers = []

    if "input" not in st.session_state:
        st.session_state.input = ""

    st.markdown(
        """
            <style>
                   .block-container {
                        padding-top: 32px;
                        padding-bottom: 32px;
                        padding-left: 0;
                        padding-right: 0;
                    }
                    .element-container img {
                        background-color: #000000;
                    }
                    .main-header {
                        font-size: 24px;
                    }
                    #MainMenu {
                        visibility: visible;
                    }
                    footer {
                        visibility: visible;
                    }
                    header {
                        visibility: visible;
                    }
            </style>
            """,
        unsafe_allow_html=True,
    )

    clear = write_top_bar()

    if clear:
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.input = ""
        st.session_state["chat_history"] = []

    with st.container():
        for q, a in zip(st.session_state.questions, st.session_state.answers):
            write_user_message(q)
            write_chat_message(a, q)

    st.markdown("---")

    if SHOW_SAMPLE_QUESTIONS:
        with st.expander("Click here for sample questions..."):
            st.markdown(
                """
                    - What is Amazon SageMaker?
                    - What are some of its major features?
                    - How do I get started using it?
                    - Tell me about Amazon SageMaker Feature Store.
                    - What does the Inference Recommender do?
                    - What is Autopilot?
                    - How much does SageMaker cost?
                """
            )
        st.markdown(" ")

    st.text_input(
        TEXT_INPUT_PROMPT,
        placeholder=TEXT_INPUT_PLACEHOLDER,
        help=TEXT_INPUT_HELP,
        key="input",
        on_change=handle_input,
    )


def write_top_bar():
    col1, col2, col3 = st.columns([1, 10, 2])
    with col1:
        st.image(HEADER_LOGO, use_column_width="always")
    with col2:
        selected_provider = sys.argv[1]
        if selected_provider in PROVIDER_MAP:
            provider = PROVIDER_MAP[selected_provider]
        else:
            provider = selected_provider.capitalize()
        # st.markdown(f"#### {HEADER_TITLE}!")
        st.markdown(f"#### {HEADER_TITLE} and {provider}!")
    with col3:
        clear = st.button("Clear Chat")
    return clear


def handle_input():
    input = st.session_state.input
    question_with_id = {"question": input, "id": len(st.session_state.questions)}
    st.session_state.questions.append(question_with_id)

    chat_history = st.session_state["chat_history"]
    if len(chat_history) == MAX_HISTORY_LENGTH:
        chat_history = chat_history[:-1]

    llm_chain = st.session_state["llm_chain"]
    chain = st.session_state["llm_app"]
    result = chain.run_chain(llm_chain, input, chat_history)
    answer = result["answer"]
    chat_history.append((input, answer))

    document_list = []
    if "source_documents" in result:
        for d in result["source_documents"]:
            if not (d.metadata["source"] in document_list):
                document_list.append((d.metadata["source"]))

    st.session_state.answers.append(
        {
            "answer": result,
            "sources": document_list,
            "id": len(st.session_state.questions),
        }
    )
    st.session_state.input = ""


def write_user_message(md):
    col1, col2 = st.columns([1, 12])

    with col1:
        st.image(USER_ICON, use_column_width="always")
    with col2:
        st.warning(md["question"])


def render_answer(answer):
    col1, col2 = st.columns([1, 12])
    with col1:
        st.image(AI_ICON, use_column_width="always")
    with col2:
        st.info(answer["answer"])


def render_sources(sources):
    col1, col2 = st.columns([1, 12])
    with col2:
        with st.expander("Sources"):
            for s in sources:
                st.write(s)


def write_chat_message(md, q):
    chat = st.container()
    with chat:
        render_answer(md["answer"])
        if SHOW_DOC_SOURCES:
            render_sources(md["sources"])


if __name__ == "__main__":
    main()
