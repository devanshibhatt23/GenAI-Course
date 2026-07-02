import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

input_text = "Hey there, I am Devanshi."

tokens = enc.encode(input_text)
print("Tokens:", tokens)

decoded_text = enc.decode(tokens)
print("Decoded text:", decoded_text)