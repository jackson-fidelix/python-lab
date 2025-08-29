import os
import numpy as np
from time import sleep
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

Data_Directory = "data"

def load_documents():
    docs = [] 
    all_types = set()
    all_skills = set()
    all_names = set()

    for fname in os.listdir(Data_Directory):
        if fname.endswith(".txt"):
            full_path = os.path.join(Data_Directory, fname)
            # print(f"Testando a função Load Documents: {full_path}")
            with open(full_path, "r", encoding="utf-8-sig") as f:
                text = f.read()
            blocks = text.split("\n\n")
            for block in blocks:
                block = block.strip()
                if block != "":
                    if isinstance(block, list):
                        block = "\n".join(block)
                    docs.append(block)

                    lines = block.split("\n")
                    for line in lines:
                        if line.lower().startswith("tipo"):
                            types_in_doc = [t.strip().lower() for t in line.split(":")[1].split(",")]
                            all_types.update(types_in_doc)
                        elif line.lower().startswith("habilidades"):
                            skill_in_doc = [s.strip().lower() for s in line.split(":")[1].split(",")]
                            all_skills.update(skill_in_doc)
                        elif line.lower().startswith("nome"):
                            name_in_doc = [n.strip().lower() for n in line.split(":")[1].split(",")]
                            all_names.update(name_in_doc)
    
    type_list = list(all_types)
    skills_list = list(all_skills)
    name_list = list(all_names)
    
    return docs, type_list, skills_list, name_list

def build_embedder():
    model_name = "Sentence-transformers/all-MiniLM-L6-v2" # modelo pré treinado do google 
    embedder = SentenceTransformer(model_name)
    return embedder

def embed_texts(texts, embedder: SentenceTransformer):
    embeddings = embedder.encode(texts, batch_size=32, convert_to_numpy=True) # batch_size é o processamento em lote
    return embeddings

def cosine_similarity(a: np.ndarray, b: np.ndarray):
    # produto escalar
    dot = np.dot(a, b)
    # normas
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def retrieve_context(query, docs, doc_embeddings, embedder, types, skills, names, top_k=5):
    query_emb = embedder.encode([query], convert_to_numpy=True)[0]

    scores = []
    for idx, value in enumerate(doc_embeddings):
        score = cosine_similarity(query_emb, value)
        doc_lower = docs[idx].lower()
        query_lower = query.lower()
        bonus = 0.5 * sum(1 for term in query_lower.split() if term in doc_lower)
        if "habilidade" in query_lower and any(skill in doc_lower for skill in skills if skill in query_lower):
            bonus += 3.0
        if "tipo" in query_lower and any(type in doc_lower for type in types if type in query_lower):
            bonus += 3.0
        scores.append((idx, score + bonus))
    
    # print(f"Testando os pontos: {scores}")
    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices =[idx for idx,_ in scores[:top_k]]
    # print(f"Testando os tres melhores indices: {top_indices}")

    query_types = [type for type in types if type in query_lower]
    query_skills = [skill for skill in skills if skill in query_lower]
    query_names = [name for name in names if name in query_lower]

    sellected = []
    for idx in top_indices:
        doc = docs[idx]
        if isinstance(doc, list): 
            doc = "\n".join(doc) 
        doc_lower = doc.lower()
        # any serve para se pelo menos um for verdade, retorna True
        if "habilidade" in query_lower and any(skill in doc_lower for skill in query_skills):
            sellected.append(doc)
        elif any(type in doc_lower for type in query_types) \
        or any(name in doc_lower for name in query_names):
            sellected.append(doc)
    
    if not sellected:
        sellected = [docs[i] if isinstance(docs[i], str) else "\n".join(docs[i]) for i in top_indices]
    # print(f"Testando os selecionados: {sellected}")
    context = "\n".join(sellected[:3]) # evitando contexto muito longo

    return context

def build_generator():
    from transformers import logging
    logging.set_verbosity_error() # mostra apenas erros e não infos e avisos
    model_name = "google/flan-t5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    gen = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=-1)
    return gen

def format_prompt(context, question, tokenizer, max_tokens=400):
    context_tokens = tokenizer(context, add_special_tokens=False)["input_ids"]
    if len(context_tokens) > max_tokens:
        context_tokens = context_tokens[:max_tokens]
        context = tokenizer.decode(context_tokens, skip_special_tokens=True, ensure_ascii=False)
    
    prompt = (
        f"Com base no contexto: {context}\n"
        f"Pergunta: {question}\n"
        "Responda APENAS com o nome do Pokémon, a habilidade, ou 'Não sei'. Sem contexto, descrições ou explicações."
    )
    return prompt

def main():
    docs, types, skills, names = load_documents()
    print("\033[7;40m Carregando documentos... \033[m")
    sleep(2)
    if len(docs) == 0:
        print("Nenhum .txt encontrado na pasta 'data'.")
        return

    print(f"\033[32m {len(docs)} documentos encontrados. Gerando embeddings com NumPy... \033[m")
    embedder = build_embedder()
    doc_embeddings = embed_texts(docs, embedder)

    generator = build_generator()
    tokenizer = generator.tokenizer # para obter o token do pipeline
    # print("Iniciializando LLM Local (flan-t5-large)")
    
    while True:
        question = input("\033[7;33m Digite sua pergunta [0 para sair]: \033[m").strip()
        print("===--==="*12)
        if question.isdigit() and int(question) == 0:
            print("\033[1;40m Agradeço pela participação no Projeto 'RAG Pokemon'. \033[m")
            sleep(1)
            print("\033[1;33m Encerrando... \033[m")
            sleep(1)
            print("\033[1;32m Programa encerrado com sucesso. Até mais! \033[m")
            break
            
        context = retrieve_context(question, docs, doc_embeddings, embedder, types, skills, names, top_k=5)
        prompt = format_prompt(context, question, tokenizer, max_tokens=400)

        # busca em feixe para melhorar as respostas 'num_beams=4'
        outputs = generator(prompt, max_new_tokens=50, do_sample=False, num_beams=4, num_return_sequences=1, clean_up_tokenization_spaces=True)
        answer = outputs[0]["generated_text"].strip()
        
        # Limpar a resposta
        words = answer.split()
        found_name = None
        found_skills = []
        query_lower = question.lower()
        
        if "habilidade" in query_lower:
            for name in names:
                if name.lower() in query_lower:
                    for doc in docs:
                        if name.lower() in doc.lower():
                            for line in doc.split("\n"):
                                if line.lower().startswith("habilidades"):
                                    skills_in_doc = [s.strip() for s in line.split(":")[1].split(",")]
                                    found_skills.extend(skills_in_doc)
                                    break
                    break
            if not found_skills:
                for skill in skills:
                    if skill.lower() in query_lower:
                        for doc in docs:
                            if skill.lower() in doc.lower():
                                for line in doc.split("\n"):
                                    if line.lower().startswith("nome"):
                                        found_name = line.split(":")[1].strip()
                                        break
                                break
                        break
        else:
            # Pergunta sobre tipos ou nomes
            for word in words:
                if word.lower() in [name.lower() for name in names]:
                    found_name = word
                    break
        
        if found_skills:
            answer = ", ".join(found_skills)
        elif found_name:
            answer = found_name
        elif answer.lower() in ["não sei", "no sei"]:
            answer = "Não sei"
        else:
            answer = "Não sei"
        
        print(f"Resposta: \033[1;32m {answer} \033[m")

if __name__ == "__main__":
    main()