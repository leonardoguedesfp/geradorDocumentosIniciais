"""Tests for qualification text parser."""

import pytest
from app.core.parser import parse_qualificacao
from tests.fixtures.qualificacoes import (
    QUALIFICACAO_1, QUALIFICACAO_2, QUALIFICACAO_3, QUALIFICACAO_4, QUALIFICACAO_5,
)


class TestParseQualificacao:
    def test_standard_format(self):
        cliente, extracted = parse_qualificacao(QUALIFICACAO_1)
        assert cliente.nome_completo == "MARIA DA SILVA SANTOS"
        assert cliente.nacionalidade == "brasileira"
        assert cliente.estado_civil == "casada"
        assert "1234567" in cliente.rg
        assert "SSP-DF" in cliente.rg
        assert cliente.cpf == "123.456.789-09"
        assert "nome_completo" in extracted
        assert "cpf" in extracted

    def test_rg_without_organ(self):
        cliente, extracted = parse_qualificacao(QUALIFICACAO_2)
        assert cliente.nome_completo == "JOÃO PEREIRA DE SOUZA"
        assert "9876543" in cliente.rg
        assert cliente.cpf == "987.654.321-00"
        assert "rg" in extracted

    def test_divorced(self):
        cliente, extracted = parse_qualificacao(QUALIFICACAO_3)
        assert cliente.estado_civil == "divorciada"
        assert cliente.nome_completo == "ANA CAROLINA FERREIRA"
        assert "IFP-RJ" in cliente.rg

    def test_widower(self):
        cliente, extracted = parse_qualificacao(QUALIFICACAO_4)
        assert cliente.estado_civil == "viúvo"
        assert "endereco" in extracted

    def test_foreign_nationality(self):
        cliente, extracted = parse_qualificacao(QUALIFICACAO_5)
        assert cliente.nacionalidade == "espanhola"
        assert cliente.nome_completo == "CARMEN RODRIGUEZ LOPEZ"

    def test_empty_text(self):
        cliente, extracted = parse_qualificacao("")
        assert cliente.nome_completo == ""
        assert len(extracted) == 0

    def test_all_extract_nome(self):
        for text in [QUALIFICACAO_1, QUALIFICACAO_2, QUALIFICACAO_3, QUALIFICACAO_4, QUALIFICACAO_5]:
            cliente, extracted = parse_qualificacao(text)
            assert "nome_completo" in extracted
            assert cliente.nome_completo != ""
