from ia_engine.llm_loader import get_groq_llm


def review_story(text: str, language: str) -> str:
    """
    Améliore une histoire générée : cohérence, style, clarté, avec support multilingue.
    """
    llm = get_groq_llm()
    lang = language

    if lang == "fr":
        prompt = (
            f"Voici une histoire pour enfants de 6 à 10 ans :\n\n{text}\n\n"
            "Réécris cette histoire en français avec plus de clarté, de cohérence et un ton narratif fluide. "
            "Fais-en une histoire de 20 à 25 phrases, avec un ton bienveillant adapté aux enfants. "
            "Garde le sens général et la structure, mais utilise un langage imagé, simple et engageant."
            "RÈGLES : pas de commentaires, pas de titre, uniquement l'histoire révisée.\n"
            "MOTS INTERDITS : excité, tuer, tué, tuée, mort, mourir, décès, sang, sanglant, arme, pistolet, fusil, couteau, massacre, torture, violenter, battre, agresser, étrangler, con, connard, idiot, imbécile, débile, merde, putain, foutre, foutu, chiant, emmerder, enfoiré, salaud, bordel, cul, bite, nique, drogue, droguer, cocaïne, héroïne, ecstasy, alcool, saoul, ivre, bourré, fumer, cigarette, joint, sexe, sexy, nu, nue, nudité, pornographie, porno, viol, pédophile, inceste, diable, démon, enfer, sorcellerie, magie noire, possession, haine, haïr, raciste, suicide, se suicider]"
        )
    else:
        prompt = (
            f"Here is a children's story for ages 6 to 10:\n\n{text}\n\n"
            "Please rewrite this story in English with improved clarity, coherence, and narrative tone. "
            "Make it 20 to 25 sentences, with a caring and suitable tone for children. "
            "Keep the meaning and structure, but use child-friendly, vivid, and fluent language."
            "RULES : No comments, no title, only reviewed story.\n"
            "FORBIDDEN WORDS: kill, killed, dead, die, death, blood, bloody, weapon, gun, knife, shoot, massacre, torture, abuse, beat, strangle, attack, stupid, idiot, dumb, moron, jerk, shit, crap, fuck, fucking, bitch, bastard, asshole, drugs, drug, cocaine, heroin, weed, ecstasy,alcohol, drunk, booze, smoke, cigarette, joint,sex, sexy, nude, naked, porn, pornography,rape, rapist, pedophile, incest,devil, demon, hell, black magic, possession,hate, hateful, racist, suicide, kill yourself"
        )

    return llm.invoke(prompt).content
