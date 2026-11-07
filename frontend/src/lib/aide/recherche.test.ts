import { describe, expect, it } from "vitest"

import { articlesPourPage, normaliser, rechercherArticles } from "@/lib/aide/recherche"
import { remplirGabarits } from "@/lib/aide/texte"
import type { ArticleAideResume } from "@/lib/aide/types"

function article(slug: string, titre: string, extra: Partial<ArticleAideResume> = {}): ArticleAideResume {
  return { slug, categorie: "autres", titre, resume: "", mots_cles: "", populaire: false, pages: [], traduit: true, ...extra }
}

const ARTICLES = [
  article("code-non-recu", "Je ne reçois pas mon code de connexion", { mots_cles: "otp, sms, spam", categorie: "connexion", pages: ["/connexion"] }),
  article("paiement-refuse", "Mon paiement a été refusé ou a échoué", { mots_cles: "montant incorrect, transaction introuvable", categorie: "paiement", pages: ["/mes-paiements", "/abonnement"] }),
  article("lire-hors-ligne", "Lire sans réseau (hors connexion)", { mots_cles: "offline, data" }),
  article("accueil", "Le tableau de bord", { pages: ["/"] }),
]

describe("normaliser", () => {
  it("retire accents, casse et ponctuation", () => {
    expect(normaliser("Reçois-tu ton CODE ?")).toBe("recois tu ton code")
    expect(normaliser("cœur")).toBe("coeur")
  })
})

describe("rechercherArticles", () => {
  it("trouve sans accent et sans majuscule", () => {
    expect(rechercherArticles(ARTICLES, "RECOIS CODE").map((a) => a.slug)).toEqual(["code-non-recu"])
  })

  it("cherche aussi dans les mots-clés", () => {
    expect(rechercherArticles(ARTICLES, "otp").map((a) => a.slug)).toEqual(["code-non-recu"])
    expect(rechercherArticles(ARTICLES, "offline").map((a) => a.slug)).toEqual(["lire-hors-ligne"])
  })

  it("accepte un début de mot et une faute de frappe", () => {
    expect(rechercherArticles(ARTICLES, "paiem").map((a) => a.slug)).toEqual(["paiement-refuse"])
    expect(rechercherArticles(ARTICLES, "refuse").map((a) => a.slug)).toEqual(["paiement-refuse"])
    expect(rechercherArticles(ARTICLES, "rembourssement").length).toBe(0)
    expect(rechercherArticles(ARTICLES, "transacton").map((a) => a.slug)).toEqual(["paiement-refuse"])
  })

  it("exige tous les mots utiles et ignore les mots vides", () => {
    expect(rechercherArticles(ARTICLES, "je ne reçois pas le code").map((a) => a.slug)).toEqual(["code-non-recu"])
    expect(rechercherArticles(ARTICLES, "code paiement")).toEqual([])
  })

  it("renvoie vide pour une requête vide ou faite de mots vides", () => {
    expect(rechercherArticles(ARTICLES, "")).toEqual([])
    expect(rechercherArticles(ARTICLES, "le la de")).toEqual([])
  })

  it("classe le titre avant le résumé", () => {
    const liste = [
      article("a", "Autre sujet", { resume: "parle de quiz" }),
      article("b", "Les quiz et le chrono"),
    ]
    expect(rechercherArticles(liste, "quiz").map((a) => a.slug)).toEqual(["b", "a"])
  })
})

describe("articlesPourPage", () => {
  it("retient les articles dont une page est le chemin ou un parent", () => {
    expect(articlesPourPage(ARTICLES, "/connexion").map((a) => a.slug)).toEqual(["code-non-recu"])
    expect(articlesPourPage(ARTICLES, "/mes-paiements").map((a) => a.slug)).toEqual(["paiement-refuse"])
  })

  it("ignore le préfixe pays et la barre finale", () => {
    expect(articlesPourPage(ARTICLES, "/cm").map((a) => a.slug)).toEqual(["accueil"])
    expect(articlesPourPage(ARTICLES, "/").map((a) => a.slug)).toEqual(["accueil"])
    expect(articlesPourPage(ARTICLES, "/connexion/").map((a) => a.slug)).toEqual(["code-non-recu"])
  })

  it("la racine « / » ne capte pas toutes les pages", () => {
    expect(articlesPourPage(ARTICLES, "/quiz").map((a) => a.slug)).toEqual([])
  })
})

describe("remplirGabarits", () => {
  it("remplace les valeurs connues et laisse les inconnues visibles", () => {
    const texte = remplirGabarits("Écris à {{site}} ({{ whatsapp }}) {{inconnu}}")
    expect(texte).not.toContain("{{site}}")
    expect(texte).not.toContain("{{ whatsapp }}")
    expect(texte).toContain("{{inconnu}}")
    expect(texte).toContain("+237 689 49 26 25")
  })
})
