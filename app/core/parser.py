"""Parse qualification text (petição inicial) to extract client data via regex."""

import re
from app.models.cliente import Cliente


def parse_qualificacao(text: str) -> tuple[Cliente, list[str]]:
    """Parse qualification text and return (Cliente, list of extracted field names).

    Expected format:
    NOME COMPLETO, nacionalidade, estado civil, portador(a) da CI NÚMERO/ÓRGÃO-UF
    e do CPF NÚMERO, residente no ENDEREÇO COMPLETO
    """
    cliente = Cliente()
    extracted = []

    text = text.strip()
    if not text:
        return cliente, extracted

    # Try to extract the full pattern
    # Pattern: NAME, nationality, marital status, portador(a) da CI RG e do CPF CPF, residente (no/na/em) ADDRESS
    pattern = (
        r"^(?P<nome>[^,]+),\s*"
        r"(?P<nacionalidade>[^,]+),\s*"
        r"(?P<estado_civil>[^,]+),\s*"
        r"portador(?:a)?\s+d[ao]\s+C\.?I\.?\s*(?P<rg>[^\s].*?)\s+"
        r"e\s+do\s+C\.?P\.?F\.?\s*(?P<cpf>[\d.\-/]+),\s*"
        r"residente\s+(?:no|na|em|n[ao]s?)?\s*(?P<endereco>.+)$"
    )

    match = re.match(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        cliente.nome_completo = match.group("nome").strip()
        extracted.append("nome_completo")

        cliente.nacionalidade = match.group("nacionalidade").strip()
        extracted.append("nacionalidade")

        cliente.estado_civil = match.group("estado_civil").strip()
        extracted.append("estado_civil")

        cliente.rg = match.group("rg").strip()
        extracted.append("rg")

        cliente.cpf = match.group("cpf").strip()
        extracted.append("cpf")

        endereco_raw = match.group("endereco").strip().rstrip(".")
        cliente.logradouro_numero = endereco_raw
        extracted.append("endereco")

        return cliente, extracted

    # Fallback: try partial extractions
    # Name: everything before the first comma
    parts = text.split(",", 1)
    if parts:
        cliente.nome_completo = parts[0].strip()
        extracted.append("nome_completo")

    # Nationality
    nat_match = re.search(r",\s*(brasileir[oa]|estrangeir[oa]|[^,]+)\s*,", text, re.IGNORECASE)
    if nat_match and "nome_completo" in extracted:
        remaining = text[len(parts[0]) + 1:]
        nat_parts = remaining.split(",", 1)
        if nat_parts:
            cliente.nacionalidade = nat_parts[0].strip()
            extracted.append("nacionalidade")

    # RG
    rg_match = re.search(r"C\.?I\.?\s*([\d.\-/]+(?:\s*/\s*\w+(?:\s*-\s*\w+)?)?)", text, re.IGNORECASE)
    if rg_match:
        cliente.rg = rg_match.group(1).strip()
        if "rg" not in extracted:
            extracted.append("rg")

    # CPF
    cpf_match = re.search(r"C\.?P\.?F\.?\s*([\d.\-/]+)", text, re.IGNORECASE)
    if cpf_match:
        cliente.cpf = cpf_match.group(1).strip()
        if "cpf" not in extracted:
            extracted.append("cpf")

    # Address after "residente"
    addr_match = re.search(r"residente\s+(?:no|na|em|n[ao]s?)?\s*(.+)$", text, re.IGNORECASE | re.DOTALL)
    if addr_match:
        cliente.logradouro_numero = addr_match.group(1).strip().rstrip(".")
        if "endereco" not in extracted:
            extracted.append("endereco")

    return cliente, extracted
