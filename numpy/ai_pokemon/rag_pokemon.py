import os
import numpy as np
from time import sleep
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import re

Data_Directory = "ai_pokemon/data"

def load_documents():
    docs = [] 
    all_types = set()
    all_skills = set()
    all_names = set()
    all_characteristics = set()

    for fname in os.listdir(Data_Directory):
        if fname.endswith(".txt"):
            full_path = os.path.join(Data_Directory, fname)
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
                            types_in_doc = [t.strip() for t in line.split(":")[1].split(",")]
                            all_types.update([t.lower() for t in types_in_doc])
                        elif line.lower().startswith("habilidades"):
                            skill_in_doc = [s.strip() for s in line.split(":")[1].split(",")]
                            all_skills.update([s.lower() for s in skill_in_doc])
                        elif line.lower().startswith("nome"):
                            name_in_doc = [n.strip() for n in line.split(":")[1].split(",")]
                            all_names.update([n.lower() for n in name_in_doc])
                        elif line.lower().startswith("descrição"):
                            desc = line.split(":")[1].strip()
                            desc = re.sub(r'[.,;!?]', '', desc)
                            words = [w.lower() for w in desc.split() if w.lower() not in {"é", "um", "que", "por", "sua", "seu", "com", "em", "para", "de", "a", "o"}]
                            keywords = [w for w in words if len(w) > 3 and w not in {"pokémon", "conhecido"}]
                            all_characteristics.update(keywords)
    
    type_list = list(all_types)
    skills_list = list(all_skills)
    name_list = list(all_names)
    char_list = list(all_characteristics)
    
    return docs, type_list, skills_list, name_list, char_list

def build_embedder():
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embedder = SentenceTransformer(model_name)
    return embedder

def embed_texts(texts, embedder: SentenceTransformer):
    embeddings = embedder.encode(texts, batch_size=32, convert_to_numpy=True)
    return embeddings

def cosine_similarity(a: np.ndarray, b: np.ndarray):
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def retrieve_context(query, docs, doc_embeddings, embedder, types, skills, names, char_list, top_k=5):
    query_emb = embedder.encode([query], convert_to_numpy=True)[0]
    query_lower = query.lower()

    scores = []
    for idx, value in enumerate(doc_embeddings):
        score = cosine_similarity(query_emb, value)
        doc_lower = docs[idx].lower()
        bonus = 0.5 * sum(1 for term in query_lower.split() if term in doc_lower)
        if "habilidade" in query_lower and any(skill in doc_lower for skill in skills if skill in query_lower):
            bonus += 6.0
        if "tipo" in query_lower and any(type in doc_lower for type in types if type in query_lower):
            bonus += 6.0
        if any(name in query_lower for name in names if name in doc_lower):
            bonus += 6.0
        if any(char in query_lower for char in char_list):
            bonus += 10.0 * sum(1 for char in char_list if char in query_lower and char in doc_lower)  # Aumentado peso
        scores.append((idx, score + bonus))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = [idx for idx, _ in scores[:top_k]]

    query_types = [type for type in types if type in query_lower]
    query_skills = [skill for skill in skills if skill in query_lower]
    query_names = [name for name in names if name in query_lower]
    query_chars = [char for char in char_list if char in query_lower]

    sellected = []
    for idx in top_indices:
        doc = docs[idx]
        if isinstance(doc, list): 
            doc = "\n".join(doc) 
        doc_lower = doc.lower()
        if any(name in doc_lower for name in query_names) \
        or any(type in doc_lower for type in query_types) \
        or any(skill in doc_lower for skill in query_skills) \
        or any(char in doc_lower for char in query_chars):
            sellected.append(doc)
    
    if not sellected:
        return ""  # Contexto vazio para forçar fallback
    context = "\n".join(sellected[:3])
    return context

def build_generator():
    from transformers import logging
    logging.set_verbosity_error()
    model_name = "google/flan-t5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    gen = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=-1)
    return gen

def format_prompt(context, question, tokenizer, max_tokens=400):
    context_tokens = tokenizer(context, add_special_tokens=False)["input_ids"]
    if len(context_tokens) > max_tokens:
        context_tokens = context_tokens[:max_tokens]
        context = tokenizer.decode(context_tokens, skip_special_tokens=True)
    
    prompt = (
        f"Contexto: {context}\n"
        f"Pergunta: {question}\n"
        "Resposta: "
    )
    return prompt

def main():
    docs, types, skills, names, char_list = load_documents()
    print("\033[7;40m Carregando documentos... \033[m")
    sleep(2)
    if len(docs) == 0:
        print("Nenhum .txt encontrado na pasta 'data'.")
        return

    print(f"\033[32m {len(docs)} documentos encontrados. Gerando embeddings com NumPy... \033[m")
    embedder = build_embedder()
    doc_embeddings = embed_texts(docs, embedder)

    generator = build_generator()
    tokenizer = generator.tokenizer
    
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
            
        context = retrieve_context(question, docs, doc_embeddings, embedder, types, skills, names, char_list, top_k=5)
        # print(f"Contexto recuperado: {context}") >> para debug
        prompt = format_prompt(context, question, tokenizer, max_tokens=400)

        outputs = generator(prompt, max_new_tokens=50, do_sample=False, num_beams=12, num_return_sequences=1, clean_up_tokenization_spaces=True)
        answer = outputs[0]["generated_text"].strip()
        # print(f"Resposta bruta do modelo: {answer}") >> para debug

        # Pós-processamento robusto
        query_lower = question.lower()
        found_names = []
        found_skills = []
        found_types = []

        invalid_patterns = [
            r"qual (pokémon é de|é o tipo|pokémon tem|é a habilidade)[\w\s]*\?",
            r"resposta:", r"contexto:", r"pergunta:", r"infelizmente ainda não conheci esse pokémon\.\.\.",
            r"não sei", r"no sei", r"é um pokémon", r"retorne apenas"
        ]
        is_invalid = any(re.search(pattern, answer.lower(), re.IGNORECASE) for pattern in invalid_patterns)

        cleaned_answer = answer
        for pattern in invalid_patterns:
            cleaned_answer = re.sub(pattern, "", cleaned_answer, flags=re.IGNORECASE).strip()
        
        # Tentar usar a resposta limpa se válida
        original_names = [l for d in docs for l in d.split("\n") if l.lower().startswith("nome") and cleaned_answer.lower() in l.lower()]
        original_skills = [l for d in docs for l in d.split("\n") if l.lower().startswith("habilidades") and cleaned_answer.lower() in l.lower()]
        original_types = [l for d in docs for l in d.split("\n") if l.lower().startswith("tipo") and cleaned_answer.lower() in l.lower()]
        
        if original_names and not is_invalid:
            found_names.append(original_names[0].split(":")[1].strip())
        elif original_skills and not is_invalid:
            found_skills.extend([s.strip() for s in original_skills[0].split(":")[1].split(",")])
        elif original_types and not is_invalid:
            found_types.extend([t.strip() for t in original_types[0].split(":")[1].split(",")])
        elif ", " in cleaned_answer and not is_invalid:
            parts = [p.strip() for p in cleaned_answer.split(",")]
            original_parts = []
            for p in parts:
                for d in docs:
                    for l in d.split("\n"):
                        if l.lower().startswith("habilidades") and p.lower() in l.lower():
                            original_parts.extend([s.strip() for s in l.split(":")[1].split(",") if s.lower() == p.lower()])
                        elif l.lower().startswith("tipo") and p.lower() in l.lower():
                            original_parts.extend([t.strip() for t in l.split(":")[1].split(",") if t.lower() == p.lower()])
            if original_parts:
                if all(p.lower() in skills for p in parts):
                    found_skills.extend(original_parts)
                elif all(p.lower() in types for p in parts):
                    found_types.extend(original_parts)

        # Extrair do contexto se a resposta for inválida ou vazia
        if not (found_names or found_skills or found_types) or is_invalid:
            for doc in context.split("\n\n"):
                doc_lower = doc.lower()
                if "habilidade" in query_lower:
                    for skill in skills:
                        if skill.lower() in query_lower and skill.lower() in doc_lower:
                            for line in doc.split("\n"):
                                if line.lower().startswith("nome"):
                                    found_names.append(line.split(":")[1].strip())
                                    break
                            break
                    for line in doc.split("\n"):
                        if line.lower().startswith("habilidades") and any(name.lower() in doc_lower for name in names if name.lower() in query_lower):
                            found_skills = [s.strip() for s in line.split(":")[1].split(",")]
                            break
                elif "tipo" in query_lower:
                    for type in types:
                        if type.lower() in query_lower and type.lower() in doc_lower:
                            for line in doc.split("\n"):
                                if line.lower().startswith("nome"):
                                    found_names.append(line.split(":")[1].strip())
                                elif line.lower().startswith("tipo") and "qual é o tipo" in query_lower:
                                    found_types = [t.strip() for t in line.split(":")[1].split(",")]
                            break
                elif any(char.lower() in query_lower for char in char_list):
                    for char in char_list:
                        if char.lower() in query_lower and char.lower() in doc_lower:
                            for line in doc.split("\n"):
                                if line.lower().startswith("nome"):
                                    found_names.append(line.split(":")[1].strip())
                                    break
                            break
                else:
                    for line in doc.split("\n"):
                        if line.lower().startswith("nome"):
                            found_names.append(line.split(":")[1].strip())
                            break

        if found_skills:
            answer = ", ".join(found_skills)
        elif found_names:
            answer = ", ".join(found_names)
        elif found_types:
            answer = ", ".join(found_types)
        else:
            answer = "Infelizmente ainda não conheci esse Pokémon..."

        print(f"Resposta: \033[1;32m {answer} \033[m")

if __name__ == "__main__":
    main()