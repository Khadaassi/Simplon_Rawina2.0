from ia_engine.nodes.scenarist import improve_prompt
from ia_engine.nodes.reviewer import review_story
from ia_engine.llm_loader import get_llm

# 1. Réponses simulées d'un enfant
user_answers = {
    "nom": "Adam",
    "créature": "dragon rigolo",
    "lieu": "village flottant",
    "thème": "fantasy"
}

# 2. Prompt enrichi
enriched_prompt = improve_prompt(user_answers)
print("\nPrompt enrichi :\n", enriched_prompt)

# 3. Génération brute avec Mistral
llm = get_llm()
raw_story = llm.invoke(
    f"Voici un prompt enrichi pour une histoire pour enfant :\n\n{enriched_prompt}\n\n"
    "Écris une histoire cohérente, magique, adaptée à un enfant de 6 à 10 ans, "
    "en 10 à 15 phrases maximum. Utilise un ton bienveillant et imagé."
).content

print("\n Histoire générée (brute) :\n", raw_story)

# 4. Relecture automatique
final_story = review_story(raw_story)
print("\nHistoire relue et améliorée :\n", final_story)
