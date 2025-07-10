from ia_engine.nodes import narrator
from ia_engine.nodes.narrator import InteractiveNarrator
from ia_engine.nodes.cleaner import review_scene_and_choices


def print_step(step, index):
    print(f"\n--- Step {index} ---")
    print(f"\nScene:\n{step['scene']}")
    if step["choices"]:
        print("\nChoices:")
        for i, choice in enumerate(step["choices"], 1):
            print(f"{i}. {choice}")


def simulate_story():
    narrator = InteractiveNarrator()

    # Configuration fictive
    config = {
        "character_name": "Moona",
        "character_type": "a courageous and beautiful princess",
        "setting": "the grand Donjon of Mythos",
        "theme": "adventure and mystery"
    }

    narrator.start_story(config)

    # Print first step
    print_step(narrator.history[-1], 1)

    for i in range(2, narrator.max_steps + 1):
        # Choix fictif, on alterne entre 1 et 2
        user_choice = "1" if i % 2 == 0 else "2"
        result = narrator.next_scene(user_choice)

        # Nettoyage texte
        scene_clean, choices_clean = review_scene_and_choices(result["scene"], result["choices"])
        step = {"scene": scene_clean, "choices": choices_clean}
        narrator.history[-1] = step  # met à jour le dernier élément avec la version nettoyée

        print_step(step, i)
    return narrator


def print_full_story(narrator):
    print("\n=== STORY COMPLETE ===")
    print("\n=== Full Story ===")
    for step in narrator.history:
        print(f"\n{step['scene']}")
    print("\n=== End of Story ===\n")

if __name__ == "__main__":
    narrator_instance = simulate_story()
    print_full_story(narrator_instance)
