from ia_engine.llm_loader import get_llm

def review_story(text: str) -> str:
    """
    Améliore une histoire générée : cohérence, style, clarté.
    """
    llm = get_llm()

    prompt = (
        f"Here is a children's story for ages 6 to 10:\n\n{text}\n\n"
        "Please rewrite this story in English with improved clarity, coherence, and narrative tone. "
        "20 to 25 sentences. With a caring and suitable ton for children"
        "Keep the meaning and structure, but use child-friendly, vivid, and fluent language."
    )

    return llm.invoke(prompt).content
