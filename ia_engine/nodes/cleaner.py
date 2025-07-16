import re
from ia_engine.llm_loader import get_groq_llm


def review_scene_and_choices(scene: str, choices: list[str]) -> tuple[str, list[str]]:
    """
    Nettoie la scène et reformate les choix de manière cohérente.
    """
    scene = scene.strip()
    scene = re.sub(r"\s+", " ", scene)
    scene = scene.replace("Scene:", "").replace("Scène :", "").strip()

    cleaned_choices = []
    for choice in choices:
        c = choice.strip()
        c = re.sub(r"^(\d+\.\s*)", "", c)

        if c.lower().startswith("will "):
            c = c[5:]
            c = c.rstrip(" ?.")
            if " or " in c:
                options = [x.strip().capitalize() for x in c.split(" or ")]
                for opt in options:
                    cleaned_choices.append(opt if opt.endswith(".") else opt + ".")
                continue
            else:
                c = c[0].upper() + c[1:] + "."
        else:
            if not c.endswith("."):
                c += "."

        cleaned_choices.append(c)

    return scene, cleaned_choices


def review_full_story(scenes: list[str], language: str) -> str:
    """
    Reprend l’ensemble des scènes et propose une version fluide et cohérente
    dans la langue actuelle de l’utilisateur.
    """
    joined = "\n".join(scenes)
    llm = get_groq_llm()

    if language == "fr":
        prompt = (
            "Tu es un éditeur d’histoires pour enfants.\n"
            "Voici une histoire complète divisée en scènes :\n\n"
            f"{joined}\n\n"
            "Réécris cette histoire en français, de façon fluide, chaleureuse et adaptée à un enfant de 6 à 10 ans. "
            "Corrige les répétitions, les formulations maladroites, et harmonise le style."
        )
    else:
        prompt = (
            "You are a children's story editor. Here is a full story split into separate scenes:\n\n"
            f"{joined}\n\n"
            "Rewrite it as a smooth story suitable for a 6–10 year old. "
            "Fix any repetition, verbosity, or awkward phrasing. Use warm, vivid language."
        )

    return llm.invoke(prompt).content.strip()
