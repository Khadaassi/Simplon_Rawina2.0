from ia_engine.llm_loader import get_groq_llm


def generate_title_from_scene(scene: str, language: str) -> str:
    """
    Utilise un LLM pour générer un titre attractif à partir de la première scène d'une histoire interactive.
    Adapte la langue au contexte (EN/FR).
    """
    lang = language
    llm = get_groq_llm()

    if lang == "fr":
        prompt = (
            "Tu es un générateur de titres pour des histoires interactives pour enfants (6–10 ans).\n\n"
            "À partir de l’introduction suivante, propose un titre court et accrocheur en français.\n"
            "Évite les numéros (comme 'Chapitre 1') et limite à 10 mots.\n\n"
            f"Introduction de l’histoire :\n{scene}\n\n"
            "Titre :"
        )
    else:
        prompt = (
            "You are a title generator for children's interactive stories (ages 6–10).\n\n"
            "Given the following story introduction, propose a short, catchy title in English.\n"
            "Avoid numbering (like 'Chapter 1') and keep the title under 10 words.\n\n"
            f"Story intro:\n{scene}\n\n"
            "Title:"
        )

    response = llm.invoke(prompt)
    return response.content.strip().strip('"')


def generate_title_from_story(story_text: str, language: str) -> str:
    """
    Utilise un LLM pour générer un titre accrocheur à partir d'une histoire complète.
    Adapte la langue au contexte (EN/FR).
    """
    lang = language
    llm = get_groq_llm()

    if lang == "fr":
        prompt = (
            "Tu es un générateur de titres pour des histoires pour enfants (6–10 ans).\n"
            "À partir de l’histoire suivante, propose un titre court et accrocheur en français.\n"
            "Sans numérotation, sans ponctuation finale, et avec moins de 10 mots.\n\n"
            f"Histoire :\n{story_text}\n\n"
            "Titre :"
        )
    else:
        prompt = (
            "You are a title generator for children's short stories (ages 6–10).\n"
            "Based on the following story, suggest a short, catchy title in English.\n"
            "Avoid numbering, keep it under 10 words, and do not include punctuation like periods.\n\n"
            f"Story:\n{story_text}\n\n"
            "Title:"
        )

    response = llm.invoke(prompt)
    return response.content.strip().strip('"')
