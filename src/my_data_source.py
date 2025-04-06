from dataclasses import dataclass
from teams.ai.tokenizers import Tokenizer
from teams.ai.data_sources import DataSource
from teams.state.state import TurnContext
from teams.state.memory import Memory
from Assistant import interagir_com_assistente  # Consulta ao assistente da OpenAI

@dataclass
class Result:
    output: str
    length: int
    too_long: bool

class MyDataSource(DataSource):
    """
    Fonte de dados baseada apenas no assistente da OpenAI.
    """

    def __init__(self, name):
        self.name = name

    def name(self):
        return self.name

    async def render_data(self, context: TurnContext, memory: Memory, tokenizer: Tokenizer, maxTokens: int):
        """
        Consulta o assistente com a entrada do usuário e encapsula a resposta como contexto.
        """
        query = memory.get('temp.input')
        if not query:
            return Result('', 0, False)

        result = ''
        resposta_assistente = await interagir_com_assistente(query)

        if resposta_assistente:
            result += f"\nResposta da IA:\n{resposta_assistente}\n"

        return Result(self.formatDocument(result), len(result), False) if result else Result('', 0, False)

    def formatDocument(self, result):
        """
        Envolve a resposta no marcador de contexto exigido pelo prompt.
        """
        return f"<context>{result}</context>"
