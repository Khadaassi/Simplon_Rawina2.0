from ia_engine.llm_loader import get_llm

class InteractiveNarrator:
    def __init__(self, history=None, step=0, max_steps=5):
        self.llm = get_llm()
        self.history = history or []
        self.step = step
        self.max_steps = max_steps

    def next_scene(self, user_choice=None):
        context = "\n".join(self.history)

        if self.step == 0:
            prompt_type = "beginning"
        elif self.step == self.max_steps - 1:
            prompt_type = "ending"
        else:
            prompt_type = "middle"

        prompt = f"""You are an interactive story narrator for children (ages 6–10).
The story so far:
{context}

The user previously chose: {user_choice if user_choice else 'No choice yet'}.

Now generate the {prompt_type} of the story, in English.

Respond in this format:
Scene:
...

Choices:
1. ...
2. ...
"""

        response = self.llm.invoke(prompt).content
        self.history.append(f"Choice: {user_choice}\n{response}" if user_choice else response)
        self.step += 1
        return response

    def is_finished(self):
        return self.step >= self.max_steps
