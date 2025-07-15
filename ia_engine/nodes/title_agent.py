from ia_engine.llm_loader import get_groq_llm

def generate_title_from_scene(scene: str) -> str:
    """
    Utilise un LLM pour générer un titre attractif à partir de la première scène d'une histoire interactive.
    """
    prompt = (
        "You are a title generator for children's interactive stories (ages 6–10).\n\n"
        "Given the following story introduction, propose a short, catchy title in English.\n"
        "Avoid numbering (like 'Chapter 1') and keep the title under 10 words.\n\n"
        f"Story intro:\n{scene}\n\n"
        "Title:"
    )

    llm = get_groq_llm()
    response = llm.invoke(prompt)
    title = response.content.strip().strip('"')  # Enlève guillemets éventuels
    return title


def generate_title_from_story(story_text: str) -> str:
    """
    Utilise un LLM pour générer un titre accrocheur à partir d'une histoire complète.
    """
    prompt = (
        "You are a title generator for children's short stories (ages 6–10).\n"
        "Based on the following story, suggest a short, catchy title in English.\n"
        "Avoid numbering, keep it under 10 words, and do not include punctuation like periods.\n\n"
        f"Story:\n{story_text}\n\n"
        "Title:"
    )

    llm = get_groq_llm()
    response = llm.invoke(prompt)
    title = response.content.strip().strip('"')
    return title
