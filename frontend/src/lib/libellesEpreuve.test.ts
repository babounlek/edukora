import { afterEach, describe, expect, it } from "vitest"

import { definirLangue } from "@/lib/i18n"
import { libelleDuree, libelleEnteteExercice, libelleNiveauExercice, libelleTitreExercice } from "./libellesEpreuve"

afterEach(async () => {
  await definirLangue("fr", { persister: false })
})

describe("niveau d'un exercice d'application", () => {
  it("en français, garde la valeur saisie", () => {
    expect(libelleNiveauExercice("facile")).toBe("facile")
    expect(libelleNiveauExercice("approfondissement")).toBe("approfondissement")
  })

  it("en anglais, traduit les trois niveaux du skill", async () => {
    await definirLangue("en", { persister: false })
    expect(libelleNiveauExercice("facile")).toBe("Easy")
    expect(libelleNiveauExercice("moyen")).toBe("Medium")
    expect(libelleNiveauExercice("approfondissement")).toBe("Challenge")
  })

  it("en anglais, reconnaît les variantes du corpus (accents, féminin, casse)", async () => {
    await definirLangue("en", { persister: false })
    expect(libelleNiveauExercice("moyenne")).toBe("Medium")
    expect(libelleNiveauExercice("faible")).toBe("Easy")
    expect(libelleNiveauExercice("élevée")).toBe("Hard")
    expect(libelleNiveauExercice("Élevé")).toBe("Hard")
    expect(libelleNiveauExercice("difficile")).toBe("Hard")
  })

  it("titre d'exercice : inchangé en français, « Exercise N » en anglais, les autres titres gardés", async () => {
    expect(libelleTitreExercice("Exercice 4")).toBe("Exercice 4")
    await definirLangue("en", { persister: false })
    expect(libelleTitreExercice("Exercice 4")).toBe("Exercise 4")
    expect(libelleTitreExercice("Exercice IV")).toBe("Exercise IV")
    expect(libelleTitreExercice("Problème")).toBe("Problème")
    expect(libelleTitreExercice("")).toBe("")
  })

  it("en-tête d'exercice : inchangé en français", () => {
    expect(libelleEnteteExercice("**Exercice 3 (7 points)**")).toBe("**Exercice 3 (7 points)**")
  })

  it("en-tête d'exercice : réécrit en anglais, au singulier comme au pluriel, décimales comprises", async () => {
    await definirLangue("en", { persister: false })
    expect(libelleEnteteExercice("**Exercice 3 (7 points)**")).toBe("**Exercise 3 (7 marks)**")
    expect(libelleEnteteExercice("**Exercice 1 (1 point)**")).toBe("**Exercise 1 (1 mark)**")
    expect(libelleEnteteExercice("**Exercice 2 (2,5 points)**")).toBe("**Exercise 2 (2.5 marks)**")
  })

  it("en-tête d'exercice sans barème : « Exercise 1 » seul", async () => {
    await definirLangue("en", { persister: false })
    expect(libelleEnteteExercice("**Exercice 1** Multiple choice questions")).toBe("**Exercise 1** Multiple choice questions")
  })

  it("en-tête d'exercice : seul l'en-tête en début de texte change, la consigne qui suit reste intacte", async () => {
    await definirLangue("en", { persister: false })
    const intro = "**Exercice 3 (7 points)**\n\nTwo cows and two goats cost 560,000 FCFA. Exercice (sic)."
    expect(libelleEnteteExercice(intro)).toBe("**Exercise 3 (7 marks)**\n\nTwo cows and two goats cost 560,000 FCFA. Exercice (sic).")
    expect(libelleEnteteExercice("Voir **Exercice 3 (7 points)**")).toBe("Voir **Exercice 3 (7 points)**")
    expect(libelleEnteteExercice("")).toBe("")
  })

  it("en anglais, une valeur inconnue s'affiche brute", async () => {
    await definirLangue("en", { persister: false })
    expect(libelleNiveauExercice("expert")).toBe("expert")
  })
})

describe("libelleDuree : un seul format (test élève Gogo : « 150 min », « 2h30 », « 2h00 », « 2h »)", () => {
  it("ramène les saisies voisines au même libellé", () => {
    expect(libelleDuree("150 min")).toBe("2 h 30")
    expect(libelleDuree("2h30")).toBe("2 h 30")
    expect(libelleDuree("2h00")).toBe("2 h")
    expect(libelleDuree("2h")).toBe("2 h")
    expect(libelleDuree("2 heures")).toBe("2 h")
    expect(libelleDuree("1h30")).toBe("1 h 30")
    expect(libelleDuree("3 h")).toBe("3 h")
  })

  it("garde les minutes seules et les durées sous l'heure", () => {
    expect(libelleDuree("90 min")).toBe("1 h 30")
    expect(libelleDuree("45 min")).toBe("45 min")
  })

  it("laisse un texte libre tel quel", () => {
    expect(libelleDuree("3 h maximum")).toBe("3 h maximum")
  })
})
