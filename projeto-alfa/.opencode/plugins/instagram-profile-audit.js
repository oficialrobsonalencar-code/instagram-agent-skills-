import { tool } from "@opencode-ai/plugin";
import { chromium } from "playwright";
import path from "node:path";

const project = "I:/Projetos/Instagram-RobsonAlencar";
const profile = "https://www.instagram.com/pastorrobsonalencar/";

export const InstagramProfileAudit = async ({ directory }) => {
  if (path.resolve(directory).toLowerCase() !== path.resolve(project).toLowerCase()) return {};
  return { tool: {
    instagram_auditar_perfil: tool({
      description: "Consulta publica da bio, destaques e grade de @pastorrobsonalencar. Somente leitura e sem login.",
      args: {},
      async execute() {
        const browser = await chromium.launch({headless: true});
        try {
          const page = await browser.newPage({locale: "pt-BR"});
          await page.goto(profile, {waitUntil: "domcontentloaded", timeout: 18000});
          const heading = page.getByRole("heading", {name: "pastorrobsonalencar", exact: true});
          if (!await heading.waitFor({timeout: 6000}).then(() => true, () => false)) {
            return JSON.stringify({url: profile, status: "perfil_nao_visivel", loginSolicitado: page.url().includes("/accounts/login")});
          }
          const expand = page.getByRole("button", {name: /^(more|mais)$/i}).first();
          if (await expand.isVisible()) await expand.click({timeout: 2000}).catch(() => {});
          const snapshot = await page.evaluate(() => {
            const main = document.querySelector("main") || document.body;
            const header = main.querySelector("header");
            const links = Array.from(main.querySelectorAll("a[href]"));
            return {
              cabecalho: header?.innerText?.trim().slice(0, 1600) ?? null,
              linksDaBio: Array.from(header?.querySelectorAll("a[href]") || []).map(a => ({texto:a.innerText.trim(), url:a.href})).filter(a => a.texto && !a.url.startsWith(location.origin)),
              destaques: links.filter(a => a.pathname.includes("/stories/highlights/")).map(a => ({titulo: a.getAttribute("aria-label") || a.innerText.trim(), url: a.href})).slice(0, 12),
              grade: links.filter(a => /\/(?:p|reel)\//.test(a.pathname)).slice(0, 9).map(a => ({url: a.href, descricao: a.getAttribute("aria-label") || a.querySelector("img")?.alt || null}))
            };
          });
          return JSON.stringify({url: profile, status: "consulta_publica", ...snapshot});
        } finally {
          await browser.close();
        }
      }
    })
  }};
};
