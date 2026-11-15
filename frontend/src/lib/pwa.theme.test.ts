import { beforeEach, describe, expect, it, vi } from "vitest"

import type { ThemeExercicesResponse } from "@/api/types"

const api = vi.hoisted(() => ({
  getCours: vi.fn(), readCours: vi.fn(), getExerciceLecture: vi.fn(),
}))
vi.mock("@/api/endpoints", async (importOriginal) => ({ ...(await importOriginal<object>()), ...api }))
vi.mock("sonner", () => ({ toast: vi.fn() }))

import { CONTENU_DE_LECTURE } from "./contenuDeLecture"
import { EXERCICES_MAX_PAR_PAQUET, estThemeDisponibleHorsLigne, nombreElementsDuPaquet, retirerTheme, tailleLisible, telechargerTheme, type PaquetTheme } from "./pwa"

const exercice = (id: number, has_access = true) => ({
  exercise_id: id, lesson_slug: "l", lesson_title: "L", lesson_year: 2024, origine: "OFFICIEL", numero_exercice: "1", has_access, fait: false,
})

function paquet(exercices = [exercice(1), exercice(2), exercice(3, false)]): PaquetTheme {
  return {
    cursusId: 4, tagId: 9, subject: "MATHS",
    liste: { tag: "derivees", cours: [{ slug: "derivees", titre: "Dérivées", duree_estimee_min: 20 }], exercices, total: exercices.length, faits: 0, contextes: [] } as ThemeExercicesResponse,
  }
}

// Un faux cache en mémoire (jsdom n'a pas la Cache API).
function installerCache() {
  const magasin = new Map<string, Response>()
  const cache = {
    put: vi.fn(async (url: string, reponse: Response) => void magasin.set(url, reponse)),
    delete: vi.fn(async (url: string) => magasin.delete(url)),
    match: vi.fn(async (url: string) => magasin.get(url)),
  }
  vi.stubGlobal("caches", { open: vi.fn(async () => cache) })
  Object.defineProperty(window, "caches", { value: { open: async () => cache }, configurable: true })
  return { magasin, cache }
}

describe("paquet « Télécharger ce thème »", () => {
  beforeEach(() => {
    Object.values(api).forEach((f) => f.mockReset().mockResolvedValue({ ok: true }))
  })

  it("compte la liste, le cours (fiche + lecture) et les exercices lisibles seulement", () => {
    expect(nombreElementsDuPaquet(paquet())).toBe(1 + 2 + 2) // l'exercice verrouillé n'est pas gardé
  })

  it("plafonne le nombre d'exercices", () => {
    const beaucoup = Array.from({ length: EXERCICES_MAX_PAR_PAQUET + 20 }, (_, i) => exercice(i + 1))
    expect(nombreElementsDuPaquet(paquet(beaucoup))).toBe(1 + 2 + EXERCICES_MAX_PAR_PAQUET)
  })

  it("écrit chaque réponse dans le cache sous les chemins que le service worker garde", async () => {
    const { magasin } = installerCache()
    const progres: number[] = []
    const echecs = await telechargerTheme(paquet(), (faits) => progres.push(faits))
    expect(echecs).toBe(0)
    expect(progres.at(-1)).toBe(5)
    const chemins = [...magasin.keys()].map((u) => new URL(u, "http://x").pathname + new URL(u, "http://x").search)
    expect(chemins).toContain("/catalog/themes/9/exercices/1/lecture/")
    expect(chemins).toContain("/access/cours/read/derivees/?compact=1")
    // Tout ce qui est écrit doit être retrouvé par la règle du worker (sinon hors connexion rien ne ressort).
    for (const u of magasin.keys()) expect(CONTENU_DE_LECTURE.test(new URL(u, "http://x").pathname)).toBe(true)
    expect(await estThemeDisponibleHorsLigne(paquet())).toBe(true)
  })

  it("compte les échecs sans abandonner le reste, et le thème n'est alors pas dit disponible", async () => {
    installerCache()
    api.getExerciceLecture.mockRejectedValueOnce(new Error("réseau"))
    const echecs = await telechargerTheme(paquet())
    expect(echecs).toBe(1)
    expect(await estThemeDisponibleHorsLigne(paquet())).toBe(false)
  })
})

describe("retirer un thème gardé", () => {
  beforeEach(() => {
    Object.values(api).forEach((f) => f.mockReset().mockResolvedValue({ ok: true }))
  })

  it("efface tout ce que le paquet avait écrit, et le thème n'est plus dit disponible", async () => {
    const { magasin } = installerCache()
    await telechargerTheme(paquet())
    expect(magasin.size).toBe(5)

    await retirerTheme(paquet())

    expect(magasin.size).toBe(0)
    expect(await estThemeDisponibleHorsLigne(paquet())).toBe(false)
  })

  it("ne laisse pas les autres entrées du cache de lecture", async () => {
    const { magasin } = installerCache()
    magasin.set("http://x/autre-chose/", new Response("{}"))
    await telechargerTheme(paquet())

    await retirerTheme(paquet())

    expect([...magasin.keys()]).toEqual(["http://x/autre-chose/"])
  })
})

describe("tailleLisible", () => {
  it.each([[500, "1 Ko"], [830 * 1024, "830 Ko"], [12.4 * 1024 * 1024, "12,4 Mo"]])("%d octets -> %s", (octets, attendu) => {
    expect(tailleLisible(octets)).toBe(attendu)
  })
})

describe("CONTENU_DE_LECTURE (R21)", () => {
  it.each([
    "/catalog/themes/9/exercices/12/lecture/",
    "/catalog/cursus/4/themes-frequents/9/exercices/",
  ])("garde %s", (chemin) => expect(CONTENU_DE_LECTURE.test(chemin)).toBe(true))

  it.each([
    "/catalog/themes/9/exercices/12/",
    "/catalog/cursus/4/themes-frequents/",
    "/catalog/cursus/4/themes-frequents/9/",
  ])("ne garde pas %s", (chemin) => expect(CONTENU_DE_LECTURE.test(chemin)).toBe(false))
})
