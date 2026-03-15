"""Tests for validators module."""

import pytest
from app.core.validators import validate_cpf, normalize_cep, normalize_name, normalize_filename, strip_fields


class TestValidateCPF:
    def test_valid_cpf(self):
        assert validate_cpf("529.982.247-25") is True

    def test_valid_cpf_digits_only(self):
        assert validate_cpf("52998224725") is True

    def test_invalid_cpf_wrong_digits(self):
        assert validate_cpf("123.456.789-00") is False

    def test_invalid_cpf_all_same(self):
        assert validate_cpf("111.111.111-11") is False

    def test_invalid_cpf_short(self):
        assert validate_cpf("123") is False

    def test_invalid_cpf_empty(self):
        assert validate_cpf("") is False

    def test_valid_cpf_with_formatting(self):
        assert validate_cpf("111.444.777-35") is True


class TestNormalizeCEP:
    def test_cep_with_dash(self):
        assert normalize_cep("70747-010") == "70747-010"

    def test_cep_without_dash(self):
        assert normalize_cep("70747010") == "70747-010"

    def test_cep_short(self):
        assert normalize_cep("123") == "123"


class TestNormalizeName:
    def test_simple_name(self):
        assert normalize_name("MARIA DA SILVA") == "Maria da Silva"

    def test_prepositions(self):
        assert normalize_name("JOAO DOS SANTOS DE SOUZA") == "Joao dos Santos de Souza"

    def test_already_correct(self):
        assert normalize_name("Ana de Oliveira") == "Ana de Oliveira"

    def test_first_word_always_capitalized(self):
        assert normalize_name("da silva") == "Da Silva"

    def test_e_preposition(self):
        assert normalize_name("MARIA E SILVA") == "Maria e Silva"


class TestNormalizeFilename:
    def test_removes_accents(self):
        assert normalize_filename("José da Silva") == "Jose_da_Silva"

    def test_removes_special_chars(self):
        assert normalize_filename("Maria (teste)") == "Maria_teste"

    def test_simple_name(self):
        assert normalize_filename("Rinaldo da Silva Soares") == "Rinaldo_da_Silva_Soares"

    def test_cedilla(self):
        assert normalize_filename("João Gonçalves") == "Joao_Goncalves"


class TestStripFields:
    def test_strips_spaces(self):
        result = strip_fields({"a": "  hello  ", "b": "world  "})
        assert result == {"a": "hello", "b": "world"}

    def test_non_string_values(self):
        result = strip_fields({"a": "  hello  ", "b": 123})
        assert result == {"a": "hello", "b": 123}
