import openai
import pandas as pd

from assets.config import key

def GPT_derive_outcomes(extracted_text):
    openai.api_key = key

    prompt = (
        "Bitte analysiere den folgenden Arztbrief und beantworte die Fragen zu den vorgegebenen Stichwörtern. "
        "Wähle zwischen 'ja', 'nein' und 'unklar', wenn die Informationen aus dem Text nicht eindeutig sind. "
        "Gib eine kurze Einschätzung ab, wenn nach dem Gesamtzustand des Patienten gefragt wird. "
        "Hier ist der Arztbrief:\n\n"
        f"{extracted_text}\n\n"
        "Bitte beantworte die folgenden Fragen basierend auf den Informationen im Arztbrief:\n\n"
        "- 'Weitere Behandlung notwendig': Ist eine weitere Behandlung notwendig? [ja/nein/unklar]\n"
        "- 'Komplikationen aufgetreten': Sind Komplikationen bei der Behandlung aufgetreten? [ja/nein/unklar]\n"
        "- 'Gesamtzustand des Patienten': Wie ist der Gesamtzustand des Patienten? [Kurze Einschätzung]\n\n"
        "Bitte strukturiere die Antworten wie folgt:\n\n"
        "[\n"
        "    'Weitere Behandlung notwendig', 'ja/nein/unklar',\n"
        "    'Komplikationen aufgetreten', 'ja/nein/unklar',\n"
        "    'Gesamtzustand des Patienten', 'Kurze Einschätzung'\n"
        "]"
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

def convert_outcomes_to_dataframe(result_string):
    if not isinstance(result_string, str):
        raise ValueError("Eingabedaten sind nicht vom Typ String")

    if not result_string.startswith("[\n    '") or not result_string.endswith("'\n]"):
        raise ValueError("Eingabedaten haben nicht das erwartete Format. Das Modell hat einen Fehler beim \
                         Strukturieren der Ergebnisse gemacht.")

    expected_keywords = [
        'Weitere Behandlung notwendig',
        'Komplikationen aufgetreten',
        'Gesamtzustand des Patienten'
    ]

    try:
        # Entferne die umgebenden Zeichen "[\n    '", "'\n]" und unnötige Whitespaces.
        clean_string = result_string.strip()[4:-3].strip()

        # Teile den String anhand von "',\n    '" um die einzelnen Paare zu erhalten.
        pairs = clean_string.split("',\n    '")

        # Erstelle eine Liste von Dictionaries für jedes Schlüssel-Wert-Paar.
        data = []
        for pair in pairs:
            # Entferne die Anführungszeichen von jedem Schlüssel-Wert-Paar.
            key_value = pair.strip("'").split("', '")
            if len(key_value) != 2:
                raise ValueError(f"Ein Paar hat nicht das erwartete 'key', 'value' Format: {pair}")
            # Füge das bereinigte Paar den Daten hinzu.
            data.append({'Stichwort': key_value[0], 'Modellvorhersage': key_value[1]})

        # Erstelle einen DataFrame aus der Liste von Dictionaries.
        dataframe = pd.DataFrame(data)

        # Überprüfe, ob alle erwarteten Stichwörter im DataFrame enthalten sind.
        missing_keywords = set(expected_keywords) - set(dataframe['Stichwort'])
        if missing_keywords:
            raise ValueError(f"Fehlende Stichwörter im DataFrame: {missing_keywords}")

        return dataframe
    except Exception as e:
        # Gib eine aussagekräftige Fehlermeldung aus, wenn ein Fehler auftritt.
        raise ValueError(f"Ein Fehler ist beim Verarbeiten der Eingabedaten aufgetreten: {e}")