class ConsultaProcessosError(Exception):
    pass


class ConfiguracaoError(ConsultaProcessosError):
    pass


class BaseNaoSuportadaError(ConsultaProcessosError):
    pass


class FonteExternaError(ConsultaProcessosError):
    pass