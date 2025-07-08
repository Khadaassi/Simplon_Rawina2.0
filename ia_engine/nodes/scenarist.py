from ia_engine.llm_loader import get_llm

def improve_prompt(user_answers: dict) -> str:
    llm = get_llm()
    context = "\n".join([f"{k}: {v}" for k, v in user_answers.items()])
    prompt = (
        f"Here are the answers from a child for creating a story:\n{context}\n\n"
        "Improve this prompt by adding helpful details and making it more imaginative, "
        "while keeping the main ideas and a childlike tone."
    )
    return llm.invoke(prompt).content
