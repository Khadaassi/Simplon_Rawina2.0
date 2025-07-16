from ia_engine.llm_loader import get_groq_llm


def improve_prompt(user_answers: dict, language: str = "en") -> str:
    llm = get_groq_llm()
    context = "\n".join([f"{k}: {v}" for k, v in user_answers.items()])

    if language == "fr":
        prompt = (
            f"Voici les réponses d’un enfant pour créer une histoire :\n{context}\n\n"
            "Améliore ce prompt en ajoutant des détails utiles et en rendant le tout plus imaginatif, "
            "tout en gardant les idées principales et un ton enfantin."
        )
    else:
        prompt = (
            f"Here are the answers from a child for creating a story:\n{context}\n\n"
            "Improve this prompt by adding helpful details and making it more imaginative, "
            "while keeping the main ideas and a childlike tone."
        )

    return llm.invoke(prompt).content
