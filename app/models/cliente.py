"""Dataclass representing a client with all required fields."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Cliente:
    nome_completo: str = ""
    nacionalidade: str = ""
    estado_civil: str = ""
    profissao: str = ""
    rg: str = ""
    cpf: str = ""
    logradouro_numero: str = ""
    complemento: str = ""
    bairro: str = ""
    cidade: str = ""
    uf: str = ""
    cep: str = ""
    email: str = ""
    telefone: str = ""
    parte_contraria: str = ""
    tipo_acao: str = ""

    def endereco_completo(self) -> str:
        """Build full address string from components."""
        parts = [self.logradouro_numero.strip()]
        complemento = self.complemento.strip()
        if complemento:
            parts[0] += f", {complemento}"
        bairro = self.bairro.strip()
        cidade = self.cidade.strip()
        uf = self.uf.strip()
        cep = self.cep.strip()
        result = f"{parts[0]} — {bairro}, {cidade} ({uf}), CEP {cep}"
        return result

    def to_placeholders(self, data_extenso: str) -> dict[str, str]:
        """Return a dict mapping placeholder names to their values."""
        return {
            "NOME_COMPLETO": self.nome_completo.strip(),
            "NACIONALIDADE": self.nacionalidade.strip(),
            "ESTADO_CIVIL": self.estado_civil.strip(),
            "PROFISSAO": self.profissao.strip(),
            "RG": self.rg.strip(),
            "CPF": self.cpf.strip(),
            "ENDERECO_COMPLETO": self.endereco_completo(),
            "EMAIL": self.email.strip(),
            "TELEFONE": self.telefone.strip(),
            "PARTE_CONTRARIA": self.parte_contraria.strip(),
            "TIPO_ACAO": self.tipo_acao.strip(),
            "DATA_EXTENSO": data_extenso,
        }
