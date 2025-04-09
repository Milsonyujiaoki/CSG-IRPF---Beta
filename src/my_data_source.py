from dataclasses import dataclass
from teams.ai.tokenizers import Tokenizer
from teams.ai.data_sources import DataSource
from teams.state.state import TurnContext
from teams.state.memory import Memory
from Assistant import interagir_com_assistente
import traceback

@dataclass
class Result:
    output: str
    length: int
    too_long: bool

class MyDataSource(DataSource):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    async def render_data(self, context: TurnContext, memory: Memory, tokenizer: Tokenizer, max_tokens: int) -> Result:
        query = memory.get("temp.input")
        if not query:
            print("[DEBUG] Nenhuma entrada encontrada em 'temp.input'.")
            return Result('', 0, False)

        print(f"[DEBUG] Entrada do usuário: {query}")
        try:
            resposta = await interagir_com_assistente(query)
            print(f"[DEBUG] Resposta do assistente: {resposta}")

            if resposta:
                texto = f"\nResposta do Assistente:\n{resposta}\n"
                return Result(self.formatDocument(texto), len(texto), False)
            else:
                return Result('', 0, False)

        except Exception as e:
            print(f"[ERRO] Falha ao interagir com assistente: {e}")
            print(traceback.format_exc())
            return Result(f"<context>Erro ao consultar o assistente: {e}</context>", 0, False)

    def formatDocument(self, texto):
        return f"<context>{texto}</context>"
