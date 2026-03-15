"""Sample qualification texts for parser testing."""

# Standard format with RG organ/UF
QUALIFICACAO_1 = (
    "MARIA DA SILVA SANTOS, brasileira, casada, portadora da CI 1234567/SSP-DF "
    "e do CPF 123.456.789-09, residente no SQN 308, Bloco A, Apt 101 — Asa Norte, "
    "Brasília (DF), CEP 70747-010"
)

# Without organ on RG
QUALIFICACAO_2 = (
    "JOÃO PEREIRA DE SOUZA, brasileiro, solteiro, portador da CI 9876543 "
    "e do CPF 987.654.321-00, residente na Rua das Flores 123 — Centro, "
    "Taguatinga (DF), CEP 72000-000"
)

# Address without complement
QUALIFICACAO_3 = (
    "ANA CAROLINA FERREIRA, brasileira, divorciada, portadora da CI 5555555/IFP-RJ "
    "e do CPF 111.222.333-44, residente em Avenida Brasil 500 — Copacabana, "
    "Rio de Janeiro (RJ), CEP 22000-000"
)

# Different marital status - viúvo
QUALIFICACAO_4 = (
    "RICARDO ALMEIDA COSTA, brasileiro, viúvo, portador da CI 3333333/SSP-GO "
    "e do CPF 444.555.666-77, residente no Setor Bueno, Rua T-50, Quadra 100, Lote 15 — "
    "Setor Bueno, Goiânia (GO), CEP 74000-000"
)

# Nationality variation - estrangeira
QUALIFICACAO_5 = (
    "CARMEN RODRIGUEZ LOPEZ, espanhola, solteira, portadora da CI V123456/PF-DF "
    "e do CPF 888.999.000-11, residente na CLN 210, Bloco B, Loja 15 — Asa Norte, "
    "Brasília (DF), CEP 70862-520"
)

ALL_QUALIFICACOES = [
    QUALIFICACAO_1, QUALIFICACAO_2, QUALIFICACAO_3, QUALIFICACAO_4, QUALIFICACAO_5,
]
