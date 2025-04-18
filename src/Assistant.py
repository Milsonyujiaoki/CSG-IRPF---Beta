import os
from dotenv import load_dotenv
import openai
import asyncio
from openai import APIConnectionError, RateLimitError, APIError, NotFoundError

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path=r"C:\Users\chat_boot\Documents\GitHub\CSG-IRPF---Beta\.env")

# Define a chave da API
openai.api_key = os.getenv('OPENAI_API_KEY')

# Inicializa o cliente assíncrono
client = openai.AsyncOpenAI(
    api_key=openai.api_key,
    max_retries=4,
    timeout=20.0
)

# Função assíncrona para interagir com o Assistente
async def interagir_com_assistente(mensagem_usuario):
    try:
        # ESCOPOS [{CorpUltron: asst_rhFLyYpv6nFMHnX7mmUzb2xv} {Teams Assistente: asst_TmB8aYjD04Tf64YvpFTIoMW4}]
        assistant = await client.beta.assistants.retrieve("asst_rhFLyYpv6nFMHnX7mmUzb2xv")
        
        # ESCOPOS [{CorpUltron:  thread_thddDtGOVSkmntnj3iDGKhh3 thread_G8ttyitsHYSb5h2nEXgWEOV6 }{Teams Assistente: thread_0b1mMFnXWkDZRuHCmNdGpE5w}]
        try:
            thread = await client.beta.threads.retrieve("thread_G8ttyitsHYSb5h2nEXgWEOV6")
        except NotFoundError:
            thread = await client.beta.threads.create()

        # Adiciona uma mensagem à thread
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=mensagem_usuario
        )

        # Executa o Assistente
        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Responda ao usuário com base na conversa anterior e com base no pdf fornecido."
        )

        # Captura a última resposta
        if run.status == "completed":
            messages = await client.beta.threads.messages.list(thread_id=thread.id)
            for msg in messages.data:
                if msg.role == "assistant":
                    return msg.content[0].text.value
            return "Nenhuma mensagem encontrada."
        elif run.status == "failed":
            return f"Erro: {getattr(run, 'error', 'Motivo desconhecido.')}"
        else:
            return f"Status da execução: {run.status}"
    
    except APIConnectionError as e:
        return f"O servidor não pôde ser alcançado: {e}"
    except RateLimitError:
        return "Erro 429: Limite de requisições excedido."
    except APIError as e:
        return f"Erro na API: {str(e)}"
    except NotFoundError:
        return "Erro: Assistente ou thread não encontrados."

