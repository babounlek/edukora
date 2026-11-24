import { describe, expect, it } from "vitest"

import { cheminPublicDeLaSource, texteDeNotePartagee } from "./partageNote"

describe("cheminPublicDeLaSource", () => {
  it("renvoie la page publique : sans section, sans paramètres, sans /lire", () => {
    expect(cheminPublicDeLaSource("/cours/lire-un-tableau/lire#regle")).toBe("/cours/lire-un-tableau")
    expect(cheminPublicDeLaSource("/cm/themes-frequents/3060/exercices/10023?subject=MATHS&cursus=14")).toBe(
      "/cm/themes-frequents/3060/exercices/10023",
    )
  })

  it("n'envoie jamais vers un quiz personnel", () => {
    expect(cheminPublicDeLaSource("/quiz/session/636")).toBe("/")
    expect(cheminPublicDeLaSource("/historique/quiz/12")).toBe("/")
    expect(cheminPublicDeLaSource(undefined)).toBe("/")
  })
})

describe("texteDeNotePartagee", () => {
  it("met en forme pour WhatsApp : gras à une étoile, pas de $, citation entre guillemets", () => {
    const texte = texteDeNotePartagee({ matiere: "Maths", note: "Retiens **Pythagore** : $a^2+b^2=c^2$", citation: "Un triangle" }, "Ma note")
    expect(texte).toBe("Ma note · Maths\n\n« Un triangle »\n\nRetiens *Pythagore* : a^2+b^2=c^2")
  })
})
