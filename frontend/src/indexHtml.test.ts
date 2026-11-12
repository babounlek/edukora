import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { describe, expect, it } from "vitest"

// index.html est le HTML initial de TOUTES les pages : y poser une donnée structurée invalide ou casser un
// %VITE_*% la rendrait illisible pour les moteurs, sans que l'application elle-même ne change.
const html = readFileSync(resolve(__dirname, "../index.html"), "utf-8")

describe("index.html : données structurées du site", () => {
  it("porte un JSON-LD valide avec l'organisation et le site, une fois les variables remplacées", () => {
    const brut = /<script type="application\/ld\+json">([\s\S]*?)<\/script>/.exec(html)?.[1]
    expect(brut).toBeTruthy()
    const remplace = (brut as string).replaceAll("%VITE_SITE_URL%", "https://edukora.africa").replaceAll("%VITE_SITE_NAME%", "EduKora")
    const donnees = JSON.parse(remplace)
    const types = donnees["@graph"].map((n: { "@type": string }) => n["@type"])
    expect(types).toEqual(["Organization", "WebSite"])
    expect(donnees["@graph"][0].logo).toBe("https://edukora.africa/pwa-512.png")
    // Le site se déclare son propre éditeur : un seul identifiant, référencé et non répété.
    expect(donnees["@graph"][1].publisher["@id"]).toBe(donnees["@graph"][0]["@id"])
  })

  it("ne laisse aucun %VITE_...% inconnu dans le JSON-LD", () => {
    const brut = /<script type="application\/ld\+json">([\s\S]*?)<\/script>/.exec(html)?.[1] as string
    const variables = [...brut.matchAll(/%(VITE_[A-Z_]+)%/g)].map((m) => m[1])
    expect(new Set(variables)).toEqual(new Set(["VITE_SITE_URL", "VITE_SITE_NAME"]))
  })
})
