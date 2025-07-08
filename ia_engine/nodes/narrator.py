from ia_engine.llm_loader import get_llm

class InteractiveNarrator:
    def __init__(self, history=None, step=0, max_steps=5):
        self.llm = get_llm()
        self.history = history or []
        self.step = step
        self.max_steps = max_steps

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
            f"The theme of the story is {theme}.\n\n"
            "Write the first scene (3-5 sentences max), then propose exactly two choices "
            "the child can make to continue the story.\n"
            "Respond in this format:\n"
            "Scene:\n...\n\nChoices:\n1. ...\n2. ..."
        )

        response = self.llm.invoke(prompt).content
        self.history.append(response)
        self.step = 1  # first step completed

    def next_scene(self, user_choice=None):
        context = "\n".join(self.history)

        if self.step >= self.max_steps:
            return "✨ The story has ended."

        prompt_type = (
            "ending" if self.step == self.max_steps - 1
            else "middle"
        )

        prompt = f"""You are continuing an interactive story for children (ages 6–10).
Story so far:
{context}

The child previously chose: {user_choice}.

Now generate the {prompt_type} of the story in English.

Respond in this format:
Scene:
...

Choices:
1. ...
2. ...
"""

        response = self.llm.invoke(prompt).content
        self.history.append(f"Choice: {user_choice}\n{response}")
        self.step += 1
        return response

    def is_finished(self):
        return self.step >= self.max_steps
