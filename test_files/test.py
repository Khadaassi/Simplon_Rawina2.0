from ia_engine.nodes.scenarist import improve_prompt

user_answers = {
    "nom_du_personnage": "Lina",
    "animal_préféré": "licorne",
    "lieu_magique": "forêt des nuages",
    "problème à résoudre": "retrouver son arc-en-ciel disparu",
}

resultat = improve_prompt(user_answers)

print("\n🎨 Prompt enrichi :\n")
print(resultat)
