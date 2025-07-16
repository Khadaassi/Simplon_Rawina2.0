from ia_engine.llm_loader import get_groq_llm


def review_story(text: str, language: str) -> str:
    """
    Améliore une histoire générée : cohérence, style, clarté, avec support multilingue.
    """
    llm = get_groq_llm()
    lang = language

    if lang == "fr":
        prompt = (
            f"Voici une histoire pour enfants de 6 à 10 ans :\n\n{text}\n\n"
            "Réécris cette histoire en français avec plus de clarté, de cohérence et un ton narratif fluide. "
            "Fais-en une histoire de 20 à 25 phrases, avec un ton bienveillant adapté aux enfants. "
            "Garde le sens général et la structure, mais utilise un langage imagé, simple et engageant."
        )
    else:
        prompt = (
            f"Here is a children's story for ages 6 to 10:\n\n{text}\n\n"
            "Please rewrite this story in English with improved clarity, coherence, and narrative tone. "
            "Make it 20 to 25 sentences, with a caring and suitable tone for children. "
            "Keep the meaning and structure, but use child-friendly, vivid, and fluent language."
        )

    return llm.invoke(prompt).content
