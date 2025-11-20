from django.shortcuts  import render
from django.http import JsonResponse
from .rag_pokemon import process_query

def chat(request):
    return render(request, 'chat_app/index.html')

def process(request):
    if request.method == 'POST':
        pergunta = request.POST.get('question', '').strip()
        if pergunta:
            resposta = process_query(pergunta) + ' '
        else:
            resposta = 'Fala alguma coisa aí! '
        return JsonResponse({'answer': resposta})
    return JsonResponse({'error': 'método inválido'}, status=400)