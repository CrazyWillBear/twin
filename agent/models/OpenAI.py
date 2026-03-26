from langchain_openai import ChatOpenAI

gpt_5_1 = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.5
)