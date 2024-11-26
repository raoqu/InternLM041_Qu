from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core.llms import ChatMessage
LLM_MODEL_NAME = "/Users/raoqu/models/internlm2-chat-1_8b"

llm = HuggingFaceLLM(
    model_name=LLM_MODEL_NAME,
    tokenizer_name=LLM_MODEL_NAME,
    model_kwargs={"trust_remote_code":True},
    tokenizer_kwargs={"trust_remote_code":True}
)

rsp = llm.chat(messages=[ChatMessage(content="2024年成都全程马拉松的终点在哪里？")])
print(rsp)