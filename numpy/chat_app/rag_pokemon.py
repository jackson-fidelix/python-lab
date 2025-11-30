import os
import numpy as np
import re
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Caminho correto para a pasta data (funciona no Django)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Data_Directory = os.path.join(BASE_DIR, "ai_pokemon", "data")


def load_documents():
    docs = []
    all_types = set()
    all_skills = set()
    all_names = set()
    all_characteristics = set()

    for fname in os.listdir(Data_Directory):
        if fname.endswith(".txt"):
            path = os.path.join(Data_Directory, fname)
            with open(path, "r", encoding="utf-8-sig") as f:
                text = f.read()

            for block in text.split("\n\n"):
                block = block.strip()
                if block:
                    docs.append(block)
                    for line in block.split("\n"):
                        l = line.lower()
                        if l.startswith("tipo:"):
                            tipos = [t.strip() for t in line.split(":", 1)[1].split(",")]
                            all_types.update(t.lower() for t in tipos)
                        elif l.startswith("habilidades:"):
                            habs = [h.strip() for h in line.split(":", 1)[1].split(",")]
                            all_skills.update(h.lower() for h in habs)
                        elif l.startswith("nome:"):
                            noms = [n.strip() for n in line.split(":", 1)[1].split(",")]
                            all_names.update(n.lower() for n in noms)
                        elif l.startswith("descrição:"):
                            desc = line.split(":", 1)[1].strip()
                            desc = re.sub(r'[.,;!?]', '', desc)
                            words = [w.lower() for w in desc.split() if w.lower() not in {"é","um","que","por","sua","seu","com","em","para","de","a","o"}]
                            keywords = [w for w in words if len(w) > 3 and w not in {"pokémon", "conhecido"}]
                            all_characteristics.update(keywords)

    return docs, list(all_types), list(all_skills), list(all_names), list(all_characteristics)

def build_embedder():
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_texts(texts, embedder):
    return embedder.encode(texts, batch_size=32, convert_to_numpy=True)

def cosine_similarity(a, b):
    dot = np.dot(a, b)
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)

def retrieve_context(query, docs, doc_embeddings, embedder, types, skills, names, char_list, top_k=5):
    query_emb = embedder.encode([query])[0]
    query_lower = query.lower()

    scores = []
    for i, emb in enumerate(doc_embeddings):
        score = cosine_similarity(query_emb, emb)
        doc_lower = docs[i].lower()
        bonus = 0.5 * sum(1 for t in query_lower.split() if t in doc_lower)

        if "habilidade" in query_lower and any(skill in doc_lower for skill in skills if skill in query_lower):
            bonus += 6.0
        if "tipo" in query_lower and any(t in doc_lower for t in types if t in query_lower):
            bonus += 6.0
        if any(n in query_lower for n in names if n in doc_lower):
            bonus += 6.0
        if any(c in query_lower for c in char_list if c in doc_lower):
            bonus += 10.0

        scores.append((i, score + bonus))

    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = [i for i, _ in scores[:top_k]]

    selected = []
    for i in top_indices:
        doc = docs[i]
        if any(term in doc.lower() for term in query_lower.split() if len(term) > 2):
            selected.append(doc)

    return "\n".join(selected[:3]) if selected else ""

def build_generator():
    from transformers import logging
    logging.set_verbosity_error()
    model_name = "google/flan-t5-large"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=-1)

def format_prompt(context, question, tokenizer, max_tokens=400):
    context_tokens = tokenizer(context, add_special_tokens=False)["input_ids"]
    if len(context_tokens) > max_tokens:
        context_tokens = context_tokens[:max_tokens]
        context = tokenizer.decode(context_tokens, skip_special_tokens=True)
    return f"Contexto: {context}\nPergunta: {question}\nResposta: "

def process_query(question: str) -> str:
    if not question.strip():
        return "Digite uma pergunta!"

    # Carrega tudo (igual ao main)
    docs, types, skills, names, char_list = load_documents()
    if len(docs) == 0:
        return "Nenhum Pokémon encontrado na pasta data/"

    embedder = build_embedder()
    doc_embeddings = embed_texts(docs, embedder)
    generator = build_generator()
    tokenizer = generator.tokenizer

    # Recupera contexto
    context = retrieve_context(question, docs, doc_embeddings, embedder, types, skills, names, char_list, top_k=5)
    if not context:
        return "Infelizmente ainda não conheci esse Pokémon..."

    prompt = format_prompt(context, question, tokenizer, max_tokens=400)

    # Gera resposta
    outputs = generator(
        prompt,
        max_new_tokens=50,
        do_sample=False,
        num_beams=12,
        num_return_sequences=1,
        clean_up_tokenization_spaces=True
    )
    answer = outputs[0]["generated_text"].strip()

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

    # Tenta validar a resposta do modelo com os documentos originais
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

    # Fallback: extrai direto do contexto se alucinou
    if not (found_names or found_skills or found_types) or is_invalid:
        for doc in context.split("\n\n"):
            doc_lower = doc.lower()
            if "habilidade" in query_lower:
                for skill in skills:
                    if skill in query_lower and skill in doc_lower:
                        for line in doc.split("\n"):
                            if line.lower().startswith("nome"):
                                found_names.append(line.split(":")[1].strip())
                                break
                        break
                for line in doc.split("\n"):
                    if line.lower().startswith("habilidades") and any(n in doc_lower for n in names if n in query_lower):
                        found_skills = [s.strip() for s in line.split(":")[1].split(",")]
                        break
            elif "tipo" in query_lower:
                for t in types:
                    if t in query_lower and t in doc_lower:
                        for line in doc.split("\n"):
                            if line.lower().startswith("nome"):
                                found_names.append(line.split(":")[1].strip())
                            elif line.lower().startswith("tipo"):
                                found_types = [tt.strip() for tt in line.split(":")[1].split(",")]
                        break
            elif any(c in query_lower for c in char_list if c in doc_lower):
                for line in doc.split("\n"):
                    if line.lower().startswith("nome"):
                        found_names.append(line.split(":")[1].strip())
                        break
            else:
                for line in doc.split("\n"):
                    if line.lower().startswith("nome"):
                        found_names.append(line.split(":")[1].strip())
                        break

    # Monta resposta final
    if found_skills:
        return ", ".join(found_skills)
    elif found_names:
        return ", ".join(found_names)
    elif found_types:
        return ", ".join(found_types)
    else:
        return "Infelizmente ainda não conheci esse Pokémon..."