class ToolRegistry:

    _tools = {}

    @classmethod
    def registrar(
        cls,
        nome: str,
        funcao
    ):
        cls._tools[nome] = funcao

    @classmethod
    def existe(
        cls,
        nome: str
    ) -> bool:
        return nome in cls._tools

    @classmethod
    def executar(
        cls,
        nome: str,
        **argumentos
    ):
        if not cls.existe(nome):
            raise ValueError(
                f"Ferramenta '{nome}' não encontrada."
            )

        return cls._tools[nome](
            **argumentos
        )

    @classmethod
    def listar(cls) -> list[str]:
        return list(
            cls._tools.keys()
        )