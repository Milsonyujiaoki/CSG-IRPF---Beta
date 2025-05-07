import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI, APIConnectionError, RateLimitError, APIError, NotFoundError

# Carrega as variáveis de ambiente
load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID", "asst_rhFLyYpv6nFMHnX7mmUzb2xv")
THREAD_ID = os.getenv("OPENAI_THREAD_ID", "thread_G8ttyitsHYSb5h2nEXgWEOV6")

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    max_retries=4,
    timeout=20.0
)

async def interagir_com_assistente(mensagem_usuario: str) -> str:
    try:
        assistant = await client.beta.assistants.retrieve(ASSISTANT_ID)

        # 🧠 Reutiliza thread se for válida, senão cria uma nova
        thread = None
        if THREAD_ID:
            try:
                thread = await client.beta.threads.retrieve(THREAD_ID)
                print(f"[DEBUG] Thread reutilizada: {thread.id}")
            except (NotFoundError, APIError) as e:
                print(f"[AVISO] Thread inválida no .env ({THREAD_ID}). Criando nova.")
                thread = await client.beta.threads.create()
                print(f"[INFO] NOVO THREAD_ID: {thread.id}")
        else:
            thread = await client.beta.threads.create()
            print(f"[INFO] THREAD_ID não definido. Nova thread criada: {thread.id}")

        print(f"[DEBUG] Pergunta: {mensagem_usuario}")

        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=mensagem_usuario
        )

        run = await client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Responda ao usuário com base na conversa anterior e nos arquivos fornecidos, se houver."
        )

        if run.status == "completed":
            messages = await client.beta.threads.messages.list(thread_id=thread.id)

            # Filtra resposta correspondente a este run
            for msg in messages.data:
                if msg.role == "assistant" and msg.run_id == run.id:
                    resposta = msg.content[0].text.value
                    print(f"[DEBUG] Resposta do Assistente: {resposta}")
                    return resposta

            return "Não foi possível encontrar a resposta gerada."
        
        elif run.status == "failed":
            motivo = getattr(run, 'error', 'Motivo desconhecido.')
            return f"Erro na execução do assistente: {motivo}"
        else:
            return f"Status do run: {run.status}"

    except APIConnectionError as e:
        return f"Erro de conexão com a OpenAI: {e}"
    except RateLimitError:
        return "Erro 429: Limite de requisições excedido."
    except APIError as e:
        return f"Erro da API: {e}"
    except NotFoundError:
        return "Erro: Assistente ou thread não encontrados."
    except Exception as e:
        return f"Erro inesperado: {e}"
