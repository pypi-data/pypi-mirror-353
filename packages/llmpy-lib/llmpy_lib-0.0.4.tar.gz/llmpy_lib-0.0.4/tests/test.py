import llmpy as lm

# Ask a single model
response = lm.ask(lm.Model.LLAMA_3_3_70B, "What is the capital of France?")
print(response)