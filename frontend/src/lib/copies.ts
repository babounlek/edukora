import type { SimulationListItem, TentativeInediteListItem } from "@/api/types"

export type GenreCopie = "annale" | "inedite" | "mini" | "defi"

/**
 * Une copie d'examen blanc, quelle que soit son origine : annale, inédite, mini-inédite ou défi de la semaine. Partagée
 * par « Mes examens blancs » et l'historique, qui doivent montrer les mêmes copies : l'historique ne listait que les
 * inédites, et un élève y lisait « Tentatives (6) » à côté de « 8 examens blancs » (audit du 2026-11-25).
 */
export interface Copie {
  cle: string
  genre: GenreCopie
  titre: string
  matiere: string
  started_at: string
  submitted_at: string | null
  note_obtenue: number | null
  bareme_snapshot: number | null
  /** Le chrono tourne et la copie n'est pas rendue. */
  enCours: boolean
  lienCopie: string
  lienResultat: string
}

export function depuisAnnale(s: SimulationListItem): Copie {
  return {
    cle: `a${s.id}`, genre: "annale", titre: s.epreuve_titre, matiere: s.matiere ?? "", started_at: s.started_at,
    submitted_at: s.submitted_at, note_obtenue: s.note_obtenue, bareme_snapshot: s.bareme_snapshot,
    enCours: Boolean(s.chrono_en_cours), lienCopie: `/simulation/${s.id}`, lienResultat: `/simulation/${s.id}/resultat`,
  }
}

export function depuisInedite(s: TentativeInediteListItem): Copie {
  return {
    cle: `i${s.id}`, genre: s.genre ?? "inedite", titre: s.epreuve_titre, matiere: s.subject_label, started_at: s.started_at,
    submitted_at: s.submitted_at, note_obtenue: s.note_obtenue, bareme_snapshot: s.bareme_snapshot,
    // Une copie libre entamée n'est pas un examen blanc : seule celle dont le chrono tourne est « en cours » ici.
    enCours: s.submitted_at === null && s.exam_mode_started_at !== null,
    lienCopie: `/inedit/tentative/${s.id}`, lienResultat: `/inedit/tentative/${s.id}/resultat`,
  }
}

/** La note d'une copie rendue, en % du barème : la seule mesure comparable d'une épreuve à l'autre. */
export function pourcentageCopie(s: Copie): number | null {
  if (s.submitted_at === null || s.note_obtenue === null || !s.bareme_snapshot) return null
  return Math.round((100 * s.note_obtenue) / s.bareme_snapshot)
}

/** Une mini-inédite ou un défi tient en quelques points : sa note ne se compare pas à celle d'une épreuve entière. */
export function estEpreuveEntiere(s: Copie): boolean {
  return s.genre === "annale" || s.genre === "inedite"
}
