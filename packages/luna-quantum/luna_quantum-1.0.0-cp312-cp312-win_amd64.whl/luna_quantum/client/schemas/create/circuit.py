from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

if TYPE_CHECKING:
    from luna_quantum.client.schemas.enums.circuit import CircuitProviderEnum
    from luna_quantum.client.schemas.qpu_token.token_provider import (
        RestAPITokenProvider,
    )


class CircuitIn(BaseModel):
    """
    Pydantic model for creation of circuits.

    Attributes
    ----------
    provider: str
        The provider for circuit solving
    provider: ProviderEnum
        The QASM circuit
    params: Dict[str, Any]
        Additional parameters
    """

    provider: CircuitProviderEnum
    circuit: str
    params: dict[str, Any] = {}
    qpu_tokens: RestAPITokenProvider | None = None
