import openai
import pandas as pd

from assets.config import key

def GPT_extract_text_and_categorize(extracted_text):
    openai.api_key = key

    prompt = (
        "Bitte analysiere den folgenden Arztbrief und extrahiere die relevanten Informationen zu den vorgegebenen Stichwörtern. "
        "Wenn du Informationen zu einem Stichwort findest, übertrage die Textstellen aus dem Arztbrief. "
        "Wenn keine Information zu einem Stichwort gefunden wird, gib 'NA' zurück. "
        "Hier ist der Arztbrief:\n\n"
        f"{extracted_text}\n\n"
        "Bitte extrahiere die Informationen zu den folgenden Stichwörtern:\n\n"
        "- 'Adressat': Empfänger des Arztbriefes\n"
        "- 'Versanddatum des Arztbriefes': Datum des Versands\n"
        "- 'Vorstellungsdatum Patient': Datum der Vorstellung des Patienten\n"
        "- 'Aufenthaltsdauer Patient': Dauer des Aufenthalts\n"
        "- 'Patientenname': Name des Patienten\n"
        "- 'Überweisungsgrund': Grund für die Überweisung\n"
        "- 'Krankengeschichte': Beschreibung der Krankengeschichte\n"
        "- 'Körperliche Untersuchung': Durchführung und Ergebnisse der körperlichen Untersuchung\n"
        "- 'Klinische Untersuchung': Durchführung und Ergebnisse der klinischen Untersuchung\n"
        "- 'Diagnostik': Durchgeführte Diagnostik\n"
        "- 'Invasive Eingriffe': Durchgeführte invasive Eingriffe\n"
        "- 'Operationen': Durchgeführte Operationen\n"
        "- 'Epikrise': Abschließende Betrachtung\n"
        "- 'Therapieempfehlung': Empfehlung für die weitere Therapie\n"
        "- 'Anhang': Vorhandensein eines Anhangs\n\n"
        "Bitte strukturiere die Antworten wie folgt und ersetze 'passende Textstellen' mit den unveränderten Textstellen aus dem Arztbrief:\n\n"
        "[\n"
        "    'Adressat', 'passende Textstellen',\n"
        "    'Versanddatum des Arztbriefes', 'passende Textstellen',\n"
        "    'Vorstellungsdatum Patient', 'passende Textstellen',\n"
        "    'Aufenthaltsdauer Patient', 'passende Textstellen',\n"
        "    'Patientenname', 'passende Textstellen',\n"
        "    'Überweisungsgrund', 'passende Textstellen',\n"
        "    'Krankengeschichte', 'passende Textstellen',\n"
        "    'Körperliche Untersuchung', 'passende Textstellen',\n"
        "    'Klinische Untersuchung', 'passende Textstellen',\n"
        "    'Diagnostik', 'passende Textstellen',\n"
        "    'Invasive Eingriffe', 'passende Textstellen',\n"
        "    'Operationen', 'passende Textstellen',\n"
        "    'Epikrise', 'passende Textstellen',\n"
        "    'Therapieempfehlung', 'passende Textstellen',\n"
        "    'Anhang', 'passende Textstellen'\n"
        "]"
    )

    response = openai.ChatCompletion.create(
      model='gpt-3.5-turbo-0125',
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extrahieren der Antwort
    antwort = response.choices[0].message['content']
    return antwort


def convert_categorization_to_dataframe(result_string):
    if not isinstance(result_string, str):
        raise ValueError("Eingabedaten sind nicht vom Typ String")

    if not result_string.startswith("[\n    '") or not result_string.endswith("'\n]"):
        raise ValueError("Eingabedaten haben nicht das erwartete Format. Das Modell hat einen Fehler beim \
                         strukturieren der Ergebnisse gemacht.")

    expected_keywords = [
        'Adressat',
        'Versanddatum des Arztbriefes',
        'Vorstellungsdatum Patient',
        'Aufenthaltsdauer Patient',
        'Patientenname',
        'Überweisungsgrund',
        'Krankengeschichte',
        'Körperliche Untersuchung',
        'Klinische Untersuchung',
        'Diagnostik',
        'Invasive Eingriffe',
        'Operationen',
        'Epikrise',
        'Therapieempfehlung',
        'Anhang'
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
            data.append({'Stichwort': key_value[0], 'Textstelle': key_value[1]})

        # Erstelle einen DataFrame aus der Liste von Dictionaries.
        dataframe = pd.DataFrame(data)

        # Überprüfe, ob alle erwarteten Stichwörter im DataFrame enthalten sind.
        missing_keywords = set(expected_keywords) - set(dataframe['Stichwort'])
        if missing_keywords:
            raise ValueError(f"Die Stichwörter entsprechend nicht den Vorgaben. Das Modell hat einen \
                             Fehler beim strukturieren der Ergebnisse gemacht: {missing_keywords}")

        return dataframe
    except Exception as e:
        # Gib eine aussagekräftige Fehlermeldung aus, wenn ein Fehler auftritt.
        raise ValueError(f"Ein Fehler ist beim Verarbeiten der Eingabedaten aufgetreten: {e}")