from ia_engine.nodes.narrator import InteractiveNarrator

narrator = InteractiveNarrator()

print("\n🌟 First Scene (Beginning):\n")
print(narrator.next_scene())

while not narrator.is_finished():
    choice = input("\nWhich option do you choose? (1 or 2): ")
    print("\n🎬 Next Scene:\n")
    print(narrator.next_scene(f"Option {choice}"))

print("\n🏁 End of the story.\n")
print("📚 Full Story History:\n")
for idx, scene in enumerate(narrator.history):
    print(f"\n🔹 Step {idx + 1}:\n{scene}")
