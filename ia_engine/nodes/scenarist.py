from ia_engine.llm_loader import get_llm

def improve_prompt(user_answers: dict) -> str:
    llm = get_llm()
    context = "\n".join([f"{k} : {v}" for k, v in user_answers.items()])
    prompt = (
        f"Voici les réponses d’un enfant pour écrire une histoire :\n{context}\n\n"
        "Améliore ce prompt en ajoutant des détails utiles et en le rendant plus inspirant, "
        "tout en gardant un ton enfantin. Ne change pas les idées principales."
    )
    return llm.invoke(prompt).content
