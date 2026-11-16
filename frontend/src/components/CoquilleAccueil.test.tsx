import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import { render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it } from "vitest"

import { definirLangue, t } from "@/lib/i18n"
import { CLE_ACCUEIL_ELEVE } from "@/lib/indiceAccueil"
import { ACCUEIL_PAYS_RE, CoquilleAccueil } from "./CoquilleAccueil"

const html = readFileSync(resolve(__dirname, "../../index.html"), "utf-8")
const CLES = ["accueil.hero_titre_debut", "accueil.hero_titre_accent", "accueil.hero_texte"] as const

afterEach(() => definirLangue("fr", { persister: false }))

describe("coquille de l'accueil : le hero est dans le HTML, puis React le reprend à l'identique", () => {
  it("index.html porte les mêmes textes que le hero, en français et en anglais", async () => {
    for (const cle of CLES) expect(html).toContain(t(cle))
    await definirLangue("en", { persister: false })
    for (const cle of CLES) expect(html).toContain(t(cle))
  })

  it("index.html lit la même clé d'indice que l'application", () => {
    expect(html).toContain(`localStorage.getItem("${CLE_ACCUEIL_ELEVE}")`)
  })

  it("le composant affiche le titre du hero", () => {
    render(<CoquilleAccueil />)
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Chaque jour, on te dit quoi réviser.")
  })

  it("ne vaut que pour l'accueil d'un pays", () => {
    expect(ACCUEIL_PAYS_RE.test("/cm")).toBe(true)
    expect(ACCUEIL_PAYS_RE.test("/cm/")).toBe(true)
    expect(ACCUEIL_PAYS_RE.test("/cm/epreuves")).toBe(false)
    expect(ACCUEIL_PAYS_RE.test("/quiz")).toBe(false)
  })
})
