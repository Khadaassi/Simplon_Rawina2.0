from ia_engine.nodes.scenarist import improve_prompt
from ia_engine.nodes.reviewer import review_story
from ia_engine.llm_loader import get_llm

user_answers = {
    "name": "Lina the cat",
    "creature": "tiger",
    "place": "jungle",
    "theme": "animals"
}

enriched_prompt = improve_prompt(user_answers)
print("\033[32m" + "\nImproved Prompt :\n" + "\033[0m", enriched_prompt)

llm = get_llm()
raw_story = llm.invoke(
    f"Here is an imporved prompt for a child's bedtime story :\n\n{enriched_prompt}\n\n"
    "Write a coherent story for a 6 to 10 years old "
    "10 to 15 sentences. With a caring and suitable ton for children"
).content

print("\033[34m" + "\n Raw Story :\n" + "\033[0m", raw_story)

final_story = review_story(raw_story)
print("\033[35m" + "\nImproved story :\n" + "\033[0m", final_story)
