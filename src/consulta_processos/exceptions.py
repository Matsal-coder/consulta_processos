class ConsultaProcessosError(Exception):
    """Erro base da aplicação."""


class ConfiguracaoError(
    ConsultaProcessosError,
):
    """Erro de configuração local."""


class BaseConsultaError(
    ConsultaProcessosError,
):
    """Erro genérico relacionado a bases processuais."""


class BaseNaoSuportadaError(
    BaseConsultaError,
):
    """Base solicitada não existe."""


class FonteExternaError(
    BaseConsultaError,
):
    """Erro de comunicação com fonte externa."""


class ProcessoNaoEncontradoError(
    BaseConsultaError,
):
    """Processo não encontrado na base."""