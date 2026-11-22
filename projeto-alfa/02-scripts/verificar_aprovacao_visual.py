# -*- coding: utf-8 -*-
"""Verifica comprovantes de auditoria visual V2. NUNCA assina ou aprova arte."""
from __future__ import annotations
import base64, binascii, datetime, hashlib, json, re
from pathlib import Path

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.serialization import load_pem_public_key, Encoding, PublicFormat
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except ImportError:
    InvalidSignature = None
    load_pem_public_key = None
    Ed25519PublicKey = None

PUBLIC_KEY_PATH = Path(__file__).resolve().parents[1] / "00-regras" / "visual-audit-public-key.pem"
DOMAIN = b"IG-VISUAL-AUDIT-V2\x00"
SIGNED_FIELDS = ("version", "alg", "key_id", "aprovado", "revisor", "job_id",
                 "account", "audited_at", "images_sha256", "caption_sha256")
REVIEWERS = frozenset({"auditor-deus", "codex-visual", "auditor-humano"})
SHA256 = re.compile(r"^[0-9a-f]{64}$")
UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


class VisualAuditError(PermissionError):
    """Erro seguro: nao inclui midias, tokens ou material criptografico."""


def canonical_bytes(receipt):
    """Mesmo esquema V2 usado pelo auditor externo apos inspecao real."""
    payload = {k: receipt[k] for k in SIGNED_FIELDS}
    return DOMAIN + json.dumps(payload, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":"), allow_nan=False).encode("utf-8")


def key_id_from_public_key(public_key):
    return hashlib.sha256(public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)).hexdigest()[:16]


def verify_visual_receipt(receipt, files, caption, job_id, account,
                          public_key_path=None):
    """Retorna True somente para auditoria assinada; caso contrario falha fechado.

    Esta rotina NAO atesta que o auditor realmente inspecionou a arte:
    a identidade e a responsabilidade da revisao pertencem ao detentor da
    chave privada externa, que nunca deve ficar disponivel ao agente.
    """
    if not isinstance(receipt, dict):
        raise VisualAuditError("AUDITORIA_VISUAL_COMPROVANTE_INVALIDO")
    if receipt.get("version") != 2 or receipt.get("alg") != "Ed25519":
        raise VisualAuditError("AUDITORIA_VISUAL_ASSINATURA_V2_OBRIGATORIA")
    if receipt.get("aprovado") is not True or receipt.get("revisor") not in REVIEWERS:
        raise VisualAuditError("AUDITORIA_VISUAL_REVISOR_OU_APROVACAO_INVALIDA")
    if not isinstance(job_id, str) or not UUID.fullmatch(job_id.lower()):
        raise VisualAuditError("AUDITORIA_VISUAL_JOB_INVALIDO")
    if receipt.get("job_id") != job_id:
        raise VisualAuditError("AUDITORIA_VISUAL_OUTRO_JOB")
    if receipt.get("account") != account or account != "pastorrobsonalencar":
        raise VisualAuditError("AUDITORIA_VISUAL_OUTRA_CONTA")
    try:
        when = datetime.datetime.fromisoformat(receipt["audited_at"])
        if when.tzinfo is None or when.utcoffset() is None:
            raise ValueError("missing tz")
        if when > datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5):
            raise ValueError("future timestamp")
    except (ValueError, TypeError, KeyError, OverflowError):
        raise VisualAuditError("AUDITORIA_VISUAL_DATA_INVALIDA") from None
    paths = [Path(x) for x in files]
    if not 1 <= len(paths) <= 10 or len({p.name for p in paths}) != len(paths):
        raise VisualAuditError("AUDITORIA_VISUAL_MIDIAS_INVALIDAS")
    try:
        expected = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    except OSError:
        raise VisualAuditError("AUDITORIA_VISUAL_MIDIAS_INDISPONIVEIS") from None
    if receipt.get("images_sha256") != expected:
        raise VisualAuditError("AUDITORIA_VISUAL_MIDIAS_MUDARAM")
    digest = hashlib.sha256(str(caption).strip().encode("utf-8")).hexdigest()
    if receipt.get("caption_sha256") != digest:
        raise VisualAuditError("AUDITORIA_VISUAL_LEGENDA_MUDOU")
    if not isinstance(receipt.get("caption_sha256"), str) or not SHA256.fullmatch(receipt["caption_sha256"]):
        raise VisualAuditError("AUDITORIA_VISUAL_HASH_INVALIDO")
    if load_pem_public_key is None:
        raise VisualAuditError("AUDITORIA_VISUAL_CRYPTOGRAPHY_NAO_INSTALADA")
    key_file = Path(public_key_path) if public_key_path is not None else PUBLIC_KEY_PATH
    try:
        # A chave publica esta fixa no ambiente confiavel, nunca indicada pelo recibo.
        public_key = load_pem_public_key(key_file.read_bytes())
        if not isinstance(public_key, Ed25519PublicKey):
            raise ValueError("wrong algorithm")
    except (OSError, ValueError, TypeError):
        raise VisualAuditError("AUDITORIA_VISUAL_CHAVE_PUBLICA_AUSENTE_OU_INVALIDA") from None
    if receipt.get("key_id") != key_id_from_public_key(public_key):
        raise VisualAuditError("AUDITORIA_VISUAL_CHAVE_DIVERGENTE")
    value = receipt.get("signature")
    if not isinstance(value, str) or not value.startswith("base64:"):
        raise VisualAuditError("AUDITORIA_VISUAL_ASSINATURA_AUSENTE")
    try:
        signature = base64.b64decode(value[7:], validate=True)
        if len(signature) != 64:
            raise ValueError("wrong Ed25519 signature length")
        public_key.verify(signature, canonical_bytes(receipt))
    except (InvalidSignature, ValueError, binascii.Error, KeyError, TypeError):
        raise VisualAuditError("AUDITORIA_VISUAL_ASSINATURA_NAO_VERIFICADA") from None
    return True
