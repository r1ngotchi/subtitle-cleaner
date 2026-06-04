import re

print("=== Subtitle Cleaner v0.1 ===")

text = input("Paste subtitle text: ")

# remove repeated words
text = re.sub(r"\b([\w']+)( \1\b)+", r'\1', text)

# remove filler words
fillers = ["um", "uh", "like"]

words = text.split()
cleaned_words = []

for word in words:
    if word.lower() not in fillers:
        cleaned_words.append(word)

text = " ".join(cleaned_words)

# capitalize first letter
text = text.capitalize()

print("\n=== Cleaned Output ===\n")
print(text)