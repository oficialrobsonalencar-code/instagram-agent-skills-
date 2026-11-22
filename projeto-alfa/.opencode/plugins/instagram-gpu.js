import { tool } from "@opencode-ai/plugin";
export const InstagramGPU = async () => ({tool:{instagram_gpu:tool({
 description:"Consulta a GPU real do Alfa via ComfyUI, sem iniciar geracao.",args:{},
 async execute(){const resultado=[];for(const url of ["http://127.0.0.1:8191","http://192.168.100.2:8188"]){try{const r=await fetch(url+"/system_stats",{signal:AbortSignal.timeout(3000)});if(!r.ok)throw Error(String(r.status));const s=await r.json();resultado.push({url,devices:s.devices.map(d=>({name:d.name,type:d.type,vram_free:d.vram_free}))});}catch{resultado.push({url,status:"servidor indisponivel"});}}return JSON.stringify(resultado);}
})}});