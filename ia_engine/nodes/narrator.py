# File: ia_engine/nodes/narrator.py
from ia_engine.llm_loader import get_groq_llm 
from ia_engine.nodes.cleaner import review_scene_and_choices, review_full_story


class InteractiveNarrator:
    def __init__(self, history=None, step=0, max_steps=5):
        self.llm = get_groq_llm()
        self.history = history or []
        self.step = step
        self.max_steps = max_steps
    def __getstate__(self):
        state = self.__dict__.copy()
        state['llm'] = None  # exclude the non-pickleable object
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        self.llm = get_groq_llm()

    def start_story(self, config: dict):
        """
        Starts the story based on user input (character name, theme, etc.).
        """
        character = config.get("character_name", "Alex")
        role = config.get("character_type", "a curious child")
        place = config.get("setting", "a mysterious forest")
        theme = config.get("theme", "adventure")

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

        # Clean with reviewer
        scene_clean, choices_clean = review_scene_and_choices(scene, choices)

        self.history.append({"scene": scene_clean, "choices": choices_clean})
        self.step += 1

        if self.step >= self.max_steps:
            final_message = "The end."
            self.history.append({"scene": final_message, "choices": []})
            return {"scene": final_message, "choices": []}
        return {"scene": scene_clean, "choices": choices_clean}

    def is_finished(self):
        return self.step >= self.max_steps

    def _format_history(self):
        """
        Converts the structured history into a flat prompt string for the LLM.
        """
        lines = []
        for i, step in enumerate(self.history):
            lines.append(f"Step {i + 1}:\nScene:\n{step['scene']}\nChoices:")
            for idx, choice in enumerate(step["choices"], start=1):
                lines.append(f"{idx}. {choice}")
        return "\n".join(lines)

    def _parse_response(self, text: str):
        """
        Parses LLM response into scene and list of choices.
        """
        parts = text.split("Choices:")
        scene = parts[0].replace("Scene:", "").strip()

        choices = []
        if len(parts) > 1:
            for line in parts[1].strip().split("\n"):
                if line.strip().startswith(("1.", "2.")):
                    choice_text = line.split(".", 1)[1].strip()
                    choices.append(choice_text)

        return scene, choices
    
    def final_story(self):
        """
        Returns the full story as a single string.
        """
        return review_full_story([step['scene'] for step in self.history])