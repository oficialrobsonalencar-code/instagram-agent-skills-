#!/usr/bin/env python3
# Agendador seguro e unitario para jobs de publicacao APROVADOS.
# Nao remove bloqueios e nunca escolhe um carrossel automaticamente.
import argparse, base64, datetime, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(r"I:\Projetos\Instagram-RobsonAlencar")
BASE = ROOT / "03-agendamentos" / "publicador"
LOCK = BASE / "BLOQUEIO-PUBLICACAO-ATIVO"
QUEUE = BASE / "fila"
JOB_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{8,80}$")

def load(job_id):
    if not JOB_PATTERN.fullmatch(job_id):
        raise ValueError("ID de agendamento invalido")
    path = QUEUE / f"{job_id}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Fila especifica nao encontrada: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if data.get("id") != job_id:
        raise ValueError("ID da fila nao confere")
    if data.get("status") != "aprovado" or not data.get("approved_by"):
        raise ValueError("PACOTE_NAO_APROVADO")
    if data.get("account") != "pastorrobsonalencar":
        raise ValueError("CONTA_DIVERGENTE")
    files = data.get("files", [])
    if not (1 <= len(files) <= 10) or not all(Path(p).is_file() for p in files):
        raise ValueError("MIDIAS_INVALIDAS")
    if not str(data.get("caption", "")).strip():
        raise ValueError("LEGENDA_AUSENTE")
    from validar_pacote_publicacao import validate_package
    problems=validate_package(data)
    if problems: raise ValueError("PACOTE_SEM_QA: "+", ".join(problems))
    due = datetime.datetime.fromisoformat(data["scheduled_at"])
    if due.tzinfo is None:
        raise ValueError("FUSO_OBRIGATORIO")
    if due.astimezone(datetime.timezone.utc) <= datetime.datetime.now(datetime.timezone.utc):
        raise ValueError("HORARIO_PASSADO")
    return data, due

def taskname(job_id):
    return "IG Robson Post Aprovado " + job_id

def powershell(script):
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    result = subprocess.run(["powershell.exe","-NoProfile","-NonInteractive","-EncodedCommand",encoded],
                            text=True,capture_output=True,encoding="utf-8",errors="replace",timeout=35)
    if result.returncode:
        raise RuntimeError("Agendador Windows falhou: "+(result.stderr or result.stdout)[-600:])
    return result.stdout.strip()

def register(job_id):
    data, due = load(job_id)
    from autorizacao_por_pacote import require_permit
    require_permit(data)
    local = due.astimezone(datetime.timezone(datetime.timedelta(hours=-3)))
    when = local.strftime("%Y-%m-%dT%H:%M:%S")
    executable = sys.executable.replace("'", "''")
    script = str(Path(__file__).resolve()).replace("'", "''")
    name = taskname(job_id).replace("'", "''")
    command = f"""
$ErrorActionPreference='Stop'
$due=[datetime]::ParseExact('{when}', 'yyyy-MM-ddTHH:mm:ss', [Globalization.CultureInfo]::InvariantCulture)
$arguments='"{script}" executar --id {job_id}'
$existing=Get-ScheduledTask -TaskName '{name}' -ErrorAction SilentlyContinue
if ($existing) {{ throw 'AGENDAMENTO_JA_EXISTENTE: verificar antes de alterar ou duplicar' }}
$action=New-ScheduledTaskAction -Execute '{executable}' -Argument $arguments
$trigger=New-ScheduledTaskTrigger -Once -At $due
# If the PC is asleep or temporarily offline, run on the next available start.
# Never retry an uncertain Instagram upload automatically.
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 8) -RestartCount 0
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
try {{
 Register-ScheduledTask -TaskName '{name}' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'Instagram: somente fila {job_id}; QA exigido; nao repete envio' -ErrorAction Stop | Out-Null
 $x=Get-ScheduledTask -TaskName '{name}' -ErrorAction Stop
 $info=Get-ScheduledTaskInfo -TaskName '{name}' -ErrorAction Stop
 if ($x.State -eq 'Disabled') {{ throw 'TAREFA_DESATIVADA' }}
 if ($info.NextRunTime -eq [datetime]::MinValue -or [math]::Abs(($info.NextRunTime-$due).TotalSeconds) -gt 60) {{ throw 'HORARIO_NAO_CONFIRMADO: '+$info.NextRunTime.ToString('o') }}
 if (-not $x.Settings.StartWhenAvailable) {{ throw 'RECUPERACAO_APOS_SUSPENSAO_NAO_CONFIGURADA' }}
 Write-Output ('CONFIRMADO '+$x.TaskName+' '+$info.NextRunTime.ToString('o'))
}} catch {{
 if (Get-ScheduledTask -TaskName '{name}' -ErrorAction SilentlyContinue) {{
  Unregister-ScheduledTask -TaskName '{name}' -Confirm:$false -ErrorAction SilentlyContinue
 }}
 throw
}}
"""
    print(powershell(command))

def execute(job_id):
    data, _ = load_for_run(job_id)
    from autorizacao_por_pacote import require_permit
    require_permit(data)
    result = subprocess.run([sys.executable,str(ROOT/"02-scripts"/"fila-publicacao.py"),"run","--only-id",job_id],
                            text=True,capture_output=True,encoding="utf-8",errors="replace",timeout=290)
    print(result.stdout[-2000:])
    if result.returncode:
        raise RuntimeError("EXECUCAO_FALHOU: "+result.stderr[-500:])
    if not (BASE/"processados"/f"{job_id}.json").is_file():
        raise RuntimeError("PUBLICACAO_NAO_CONFIRMADA - inspecionar a pasta revisar; nao repetir cegamente")
    print("PUBLICACAO_CONFIRMADA",job_id)

def load_for_run(job_id):
    if not JOB_PATTERN.fullmatch(job_id):
        raise ValueError("ID invalido")
    path = QUEUE/f"{job_id}.json"
    if not path.is_file():
        raise FileNotFoundError("Fila especifica nao encontrada; sem nova tentativa")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if data.get("id")!=job_id or data.get("status")!="aprovado" or not data.get("approved_by"):
        raise ValueError("APROVACAO_AUSENTE")
    if data.get("account")!="pastorrobsonalencar":
        raise ValueError("CONTA_DIVERGENTE")
    due=datetime.datetime.fromisoformat(data["scheduled_at"])
    if due.tzinfo is None:raise ValueError("FUSO_AUSENTE")
    if due.astimezone(datetime.timezone.utc)>datetime.datetime.now(datetime.timezone.utc):
        raise ValueError("AINDA_NAO_E_HORARIO")
    files=data.get("files",[])
    if not 1<=len(files)<=10 or not all(Path(x).is_file() for x in files):
        raise ValueError("MIDIA_INDISPONIVEL")
    if not str(data.get("caption","")).strip():raise ValueError("SEM_LEGENDA")
    from validar_pacote_publicacao import validate_package
    problems=validate_package(data)
    if problems: raise ValueError("PACOTE_SEM_QA: "+", ".join(problems))
    return data,due

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("modo",choices=["agendar","executar","verificar"])
    parser.add_argument("--id",required=True)
    a=parser.parse_args()
    try:
        if a.modo=="agendar":register(a.id)
        elif a.modo=="executar":execute(a.id)
        else:
            data,due=load(a.id)
            from autorizacao_por_pacote import require_permit
            require_permit(data)
            print("APTO",data["id"],due.isoformat())
    except Exception as exc:
        print("ERRO",str(exc),file=sys.stderr)
        sys.exit(1)
