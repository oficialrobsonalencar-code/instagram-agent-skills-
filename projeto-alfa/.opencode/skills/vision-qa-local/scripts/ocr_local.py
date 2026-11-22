#!/usr/bin/env python3
"""OCR local read-only: no image modifications, no generation."""
import argparse,json,sys,hashlib,io
from pathlib import Path
import pytesseract
from PIL import Image,ImageOps
def main():
 parser=argparse.ArgumentParser(description="OCR local verificavel sem gerar imagens")
 parser.add_argument("images",nargs="+")
 parser.add_argument("--lang",default="por+eng")
 args=parser.parse_args()
 valid=True
 local_tessdata=Path(__file__).resolve().parents[1]/"tessdata"
 config=f"--tessdata-dir {local_tessdata.as_posix()} --psm 6" if (local_tessdata/"por.traineddata").is_file() else "--psm 6"
 available=pytesseract.get_languages(config=f"--tessdata-dir {local_tessdata.as_posix()}" if (local_tessdata/"por.traineddata").is_file() else "")
 requested=args.lang.split("+")
 language="por" if "por" in available and "por" in requested else (args.lang if all(x in available for x in requested) else ("eng" if "eng" in available else available[0]))
 for name in args.images:
  p=Path(name)
  try:
   raw=p.read_bytes()
   img=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
   txt=pytesseract.image_to_string(img,lang=language,config=config)
   print(json.dumps({"arquivo":str(p),"sha256":hashlib.sha256(raw).hexdigest(),
                     "formato_detectado":Image.open(io.BytesIO(raw)).format,
                     "dimensoes":list(img.size),"idioma_solicitado":args.lang,"idioma_efetivo":language,
                     "aviso":"Idioma solicitado indisponivel; fallback efetuado" if language!=args.lang else None,
                     "texto_ocr":txt.strip(),"status":"OCR_CONCLUIDO","confiabilidade":"requer_conferencia_visual"},ensure_ascii=False),flush=True)
  except Exception as exc:
   valid=False
   print(json.dumps({"arquivo":name,"status":"ERRO","erro":str(exc)},ensure_ascii=False),flush=True)
 return 0 if valid else 2
if __name__=="__main__":sys.exit(main())
