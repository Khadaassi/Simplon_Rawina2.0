import re
from ia_engine.llm_loader import get_groq_llm

def review_scene_and_choices(scene: str, choices: list[str]) -> tuple[str, list[str]]:
    """
    Cleans the scene and reformats choices into consistent, action-oriented statements.
    """
    # Clean scene
    scene = scene.strip()
    scene = re.sub(r"\s+", " ", scene)
    scene = scene.replace('Scene:', '').strip()

    # Clean choices
    cleaned_choices = []
    for choice in choices:
        c = choice.strip()

        # Remove leading numbers or punctuation
        c = re.sub(r"^(\d+\.\s*)", "", c)

        # Convert question to statement if needed
        if c.lower().startswith("will "):
            # Turn "Will Moona go explore the cave?" -> "Moona goes to explore the cave."
            c = c[5:]  # Remove "Will "
            c = c.rstrip(" ?.")
            # Add basic transformation (can be improved)
            if " or " in c:
                options = [x.strip().capitalize() for x in c.split(" or ")]
                for opt in options:
                    cleaned_choices.append(opt if opt.endswith('.') else opt + '.')
                continue
            else:
                c = c[0].upper() + c[1:] + "."
        else:
            if not c.endswith("."):
                c += "."
        
        cleaned_choices.append(c)

    return scene, cleaned_choices

def review_full_story(scenes: list[str]) -> str:
    """
    Reprend l’ensemble des scènes et propose une version fluide et cohérente.
    """
    joined = "\n".join(scenes)
    prompt = (
        "You are a children's story editor. Here is a full story split into separate scenes:\n\n"
        f"{joined}\n\n"
        "Rewrite it as a smooth story suitable for a 6–10 year old. "
        "Fix any repetition, verbosity, or awkward phrasing. Use warm, vivid language."
    )
    llm = get_groq_llm()
    return llm.invoke(prompt).content.strip()