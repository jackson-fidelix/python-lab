print("**"*25)
print("Tarefa M1L1 - T3 (resolvendo traduções modernas)")
print("**"*25)

word = input('Digite uma palavra que você não entende: ').upper()

meme_dict = {
    "BETINHA": "O cara que fica moscando...",
    "MOSCAR": "o cara que é desligado, não tem atenção",
    "SIGMA": "Uma pessoa de respeito!"
}

if word in meme_dict:
    print(meme_dict[word])
else:
    print("Infelizmente nem nós sabemos essa! kkkkkk")
