from ia_engine.llm_loader import get_groq_llm
from ia_engine.nodes.cleaner import review_scene_and_choices, review_full_story


class InteractiveNarrator:
    def __init__(self, history=None, step=0, max_steps=5, language=None):
        self.llm = get_groq_llm()
        self.history = history or []
        self.step = step
        self.max_steps = max_steps
        self.language = language

    def __getstate__(self):
        state = self.__dict__.copy()
        state["llm"] = None
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        self.llm = get_groq_llm()

    def start_story(self, config: dict):
        character = config.get("character_name", "Alex")
        role = config.get("character_type", "a curious child")
        place = config.get("setting", "a mysterious forest")
        theme = config.get("theme", "adventure")

        if self.language == "fr":
            prompt = (
                f"Tu es un narrateur interactif pour une histoire pour enfants.\n"
                f"Crée la scène d'ouverture d'une histoire destinée à un enfant de 6 à 10 ans.\n\n"
                f"Le personnage principal est {character}, {role}, qui vit dans {place}.\n"
                f"Le thème de l'histoire est {theme}. Tu dois t’y tenir.\n\n"
                f"Utilise ces éléments pour créer le monde de l’histoire et introduire le personnage.\n"
                "Écris une première scène (5 à 10 phrases maximum), puis propose exactement deux choix "
                "que l'enfant peut faire pour continuer l'histoire.\n"
                "Les deux choix doivent être orientés vers l’action et adaptés à un enfant.\n"
                "Utilise ce format :\n"
                "Chapitre :\n...\n\nChoix :\n1. ...\n2. ..."
            )
        else:
            prompt = (
                f"You are an interactive narrator for a children's story.\n"
                f"Create the opening scene of a story for a child aged 6 to 10.\n\n"
                f"The main character is {character}, {role}, who lives in {place}.\n"
                f"The theme of the story is {theme}. You need to stick to the theme.\n\n"
                "Use the description to create the story's world and introduce the character.\n"
                "Write the first scene (5 to 10 sentences max), then propose exactly two choices "
                "the child can make to continue the story.\n"
                "Both choices should be action-oriented and suitable for a child.\n"
                "Use this format:\n"
                "Chapter:\n...\n\nChoices:\n1. ...\n2. ..."
            )

        response = self.llm.invoke(prompt).content
        scene, choices = self._parse_response(response)
        self.history.append({"scene": scene, "choices": choices})
        self.step = 1

    def next_scene(self, user_choice=None):
        context_str = self._format_history()
        prompt_type = "ending" if self.step == self.max_steps - 1 else "middle"
        lang = self.language

        if lang == "fr":
            prompt = (
                f"Tu continues une histoire interactive pour enfants (6–10 ans).\n"
                f"Histoire jusqu’ici :\n{context_str}\n\n"
                f"L’enfant a choisi : {user_choice}.\n"
                f"Génère maintenant la scène suivante ({prompt_type}).\n\n"
                "Utilise ce format :\n"
                "Scène :\n...\n\nChoix :\n1. ...\n2. ..."
            )
        else:
            prompt = (
                f"You are continuing an interactive story for children (ages 6–10).\n"
                f"Story so far:\n{context_str}\n\n"
                f"The child previously chose: {user_choice}.\n"
                f"Now generate the {prompt_type} of the story.\n\n"
                "Use this format:\n"
                "Scene:\n...\n\nChoices:\n1. ...\n2. ..."
            )

        response = self.llm.invoke(prompt).content
        scene, choices = self._parse_response(response)
        scene_clean, choices_clean = review_scene_and_choices(scene, choices, language=self.language)

        self.history.append({"scene": scene_clean, "choices": choices_clean})
        self.step += 1

        if self.step >= self.max_steps:
            final_message = "La fin." if lang == "fr" else "The end."
            self.history.append({"scene": final_message, "choices": []})
            return {"scene": final_message, "choices": []}
        return {"scene": scene_clean, "choices": choices_clean}

    def is_finished(self):
        return self.step >= self.max_steps

    def _format_history(self):
        lines = []
        for i, step in enumerate(self.history):
            lines.append(f"Step {i + 1}:\nScene:\n{step['scene']}\nChoices:")
            for idx, choice in enumerate(step["choices"], start=1):
                lines.append(f"{idx}. {choice}")
        return "\n".join(lines)

    def _parse_response(self, text: str):
        parts = text.split("Choices:") if "Choices:" in text else text.split("Choix :")
        scene = parts[0].replace("Scene:", "").replace("Scène :", "").replace("Chapter:", "").replace("Chapitre :", "").strip()
        choices = []

        if len(parts) > 1:
            for line in parts[1].strip().split("\n"):
                if line.strip().startswith(("1.", "2.")):
                    choice_text = line.split(".", 1)[1].strip()
                    choices.append(choice_text)

        return scene, choices

    def final_story(self):
        return review_full_story([step["scene"] for step in self.history], self.language)
