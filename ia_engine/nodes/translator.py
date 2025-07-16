from ia_engine.llm_loader import get_groq_llm

def translate_story(text: str, language: str) -> str:
    """
    Traduit une histoire générée dans l'autre langue.
    `language` = langue cible (fr ou en)
    """
    llm = get_groq_llm()

    if language == "fr":
        # Texte d'origine en anglais
        prompt = (
            f"Here is a children's story in English:\n\n{text}\n\n"
            "Please translate it into French with a smooth, vivid and child-friendly tone. "
            "No extra comments. Only the story. Use fluent, natural French."
        )
    elif language == "en":
        # Texte d'origine en français
        prompt = (
            f"Voici une histoire pour enfants en français :\n\n{text}\n\n"
            "Traduits cette histoire en anglais. Sois fluide, clair, et adapté à un enfant de 6 à 10 ans. "
            "Pas de commentaire, uniquement l'histoire."
        )
    else:
        raise ValueError(f"Unsupported language: {language}")

    return llm.invoke(prompt).content.strip()

