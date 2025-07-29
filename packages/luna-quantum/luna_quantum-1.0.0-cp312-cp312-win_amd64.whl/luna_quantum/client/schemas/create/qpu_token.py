from pydantic import BaseModel, Extra


class QpuTokenIn(BaseModel):
    """
    Pydantic model for creation QPU token.

    Attributes
    ----------
    name: str
        Name of the QPU token
    provider: ProviderEnum
        Name of provider
    token: str
        Token
    """

    name: str
    provider: str
    token: str

    class Config:
        """Pydantic configuration class."""

        extra = Extra.forbid
