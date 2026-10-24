import hashlib
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError
from pypdf import PdfReader

from .models import ConfiguracaoIA


Image.MAX_IMAGE_PIXELS = 25_000_000


class ArquivoInvalido(ValueError):
    pass


def hash_arquivo(conteudo):
    return hashlib.sha256(conteudo).hexdigest()


def preparar_arquivo(conteudo, mime, lado_maximo=2048):
    configuracao = ConfiguracaoIA.obter()
    limite = configuracao.tamanho_maximo_mb * 1024 * 1024
    if len(conteudo) > limite:
        raise ArquivoInvalido("O arquivo excede o tamanho máximo permitido.")

    if mime == "application/pdf" or conteudo.startswith(b"%PDF-"):
        try:
            paginas = len(PdfReader(BytesIO(conteudo)).pages)
        except Exception as exc:
            raise ArquivoInvalido("O PDF não pôde ser lido.") from exc
        if paginas > configuracao.pdf_max_paginas:
            raise ArquivoInvalido("O PDF excede o número máximo de páginas.")
        return conteudo, "application/pdf"

    if not mime.startswith("image/"):
        raise ArquivoInvalido("Tipo de arquivo não permitido.")
    try:
        with Image.open(BytesIO(conteudo)) as imagem:
            imagem = ImageOps.exif_transpose(imagem).convert("RGB")
            imagem.thumbnail((lado_maximo, lado_maximo))
            saida = BytesIO()
            imagem.save(saida, format="JPEG", quality=85)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ArquivoInvalido("A imagem não pôde ser processada.") from exc
    return saida.getvalue(), "image/jpeg"
