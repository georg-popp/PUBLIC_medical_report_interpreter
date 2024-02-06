import openai

from assets.config import key

def GPT_summarize_and_simplify(extracted_text):
    openai.api_key = key

    prompt = (
        "Bitte fasse die genaue Diagnose und den weiteren Therapieverlauf aus diesem Arztbrief in einfacher, \
            freundliche und sachlicher Sprache auf maximal 300 Zeichen zusammen"
        "Beginne mit \"Patient*in ...\""
        f"{extracted_text}\n\n"
    )

    response = openai.ChatCompletion.create(
    model='gpt-4-0125-preview',
    messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extrahieren Sie die Antwort
    antwort = response.choices[0].message['content']
    return antwort