#!/usr/bin/env python3
"""Validador read-only de layout de carrosseis contra uma imagem de referencia."""
from pathlib import Path
import argparse,json,sys,importlib.util
ROOT=Path(r"I:\Projetos\Instagram-RobsonAlencar")
SOURCE=ROOT/"06-referencias/layout-referencia-saveclip.json"
MEASURER=Path.home()/".config/opencode/inspect_layout_geometry.py"
def load_measurer():
    spec=importlib.util.spec_from_file_location("geom",MEASURER)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
def validate(measurement,template):
    w,h=measurement["size"]
    reference_w,reference_h=template["dimensoes"]
    if abs(w/h-reference_w/reference_h)>0.005:
        return ["Proporcao incorreta: o modelo e 4:5"]
    groups=measurement["blocos"]
    top=[b for b in groups if b["region"]=="topo"]
    body=[b for b in groups if b["region"]=="corpo"]
    foot=[b for b in groups if b["region"]=="rodape"]
    errors=[]
    if not top:errors.append("Seta superior nao detectada")
    if not body:errors.append("Nenhum bloco de texto escuro detectado")
    if not foot:errors.append("Assinatura inferior nao detectada")
    if errors:return errors
    def normalize(b):
        return [b["bbox"][0]/w,b["bbox"][1]/h,b["bbox"][2]/w,b["bbox"][3]/h]
    def expected(k):
        a=template["areas"][k]
        return [a[0]/reference_w,a[1]/reference_h,a[2]/reference_w,a[3]/reference_h]
    def center_x(v):return (v[0]+v[2])/2
    def center_y(v):return (v[1]+v[3])/2
    def check_anchor(name,block,tol_center_x=.013,tol_center_y=.015,tol_size=.018):
        actual=normalize(block);exp=expected(name)
        if abs(center_x(actual)-center_x(exp))>tol_center_x:
            errors.append(name+": deslocamento horizontal acima do limite")
        if abs(center_y(actual)-center_y(exp))>tol_center_y:
            errors.append(name+": deslocamento vertical acima do limite")
        if abs((actual[2]-actual[0])-(exp[2]-exp[0]))>tol_size:
            errors.append(name+": largura inconsistente com a referencia")
        if abs((actual[3]-actual[1])-(exp[3]-exp[1]))>tol_size:
            errors.append(name+": altura inconsistente com a referencia")
    check_anchor("seta",top[0])
    check_anchor("assinatura",foot[-1])
    body_bbox=[min(x["bbox"][0] for x in body),min(x["bbox"][1] for x in body),
               max(x["bbox"][2] for x in body),max(x["bbox"][3] for x in body)]
    c_x=(body_bbox[0]+body_bbox[2])/2/w
    expected_c_x=(template["centros_x_px"]["titulo"]+template["centros_x_px"]["complemento"])/2/reference_w
    if abs(c_x-expected_c_x)>.018:errors.append("Texto central deslocado em mais de 1,8% da largura")
    if body_bbox[0]<.065*w or body_bbox[2]>.935*w:
        errors.append("Texto invade a margem lateral segura (6,5% da largura)")
    center_body=(body_bbox[1]+body_bbox[3])/2/h
    ref_box=template["areas"]["titulo"],template["areas"]["complemento"]
    ref_center=(ref_box[0][1]+ref_box[1][3])/2/reference_h
    if abs(center_body-ref_center)>.04:
        errors.append("Bloco principal deslocado mais de 4% da altura do modelo")
    if len(body)==2:
        space=body[1]["bbox"][1]-body[0]["bbox"][3]
        ratio=space/h
        if ratio<.005 or ratio>.035:
            errors.append("Espacamento titulo/complemento fora de faixa razoavel: "+str(space)+" px")
    return errors
def main():
    ap=argparse.ArgumentParser(description="Compara posicoes e margens com o layout aprovado; nao gera imagens.")
    ap.add_argument("candidates",nargs="+")
    args=ap.parse_args()
    tpl=json.loads(SOURCE.read_text(encoding="utf-8"))
    measurer=load_measurer()
    records=[]
    for p in args.candidates:
        try:
            m=measurer.measure(p)
            errors=validate(m,tpl)
            records.append({"arquivo":p,"resultado":"REPROVADO" if errors else "GEOMETRIA_OK","erros":errors,
                            "observacao":"Aprovacao geometrica nao substitui QA de texto, cores ou fonte exata"})
        except Exception as e:
            records.append({"arquivo":p,"resultado":"ERRO","erros":[str(e)]})
    print(json.dumps(records,ensure_ascii=False,indent=2))
    return 0 if all(x["resultado"]=="GEOMETRIA_OK" for x in records) else 2
if __name__=="__main__":sys.exit(main())
