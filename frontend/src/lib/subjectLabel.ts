// Libellés compacts pour une pastille de filtre à largeur contrainte (voir
// lib/subjectIcon.ts pour la liste de référence des codes, alimentée par
// catalog.management.commands.seed_country.SUBJECTS côté backend).
const SUBJECT_SHORT_LABELS: Record<string, string> = {
  MATHS: "Maths",
  PHYSIQUE: "Physique",
  CHIMIE: "Chimie",
  PHYSIQUE_CHIMIE: "PC",
  PHYSIQUE_CHIMIE_TECH: "PCT",
  SVT: "SVT",
  FRANCAIS: "Français",
  PHILOSOPHIE: "Philo",
  HISTOIRE: "Histoire",
  GEOGRAPHIE: "Géo",
  HISTOIRE_GEO: "Histoire-Géo",
  ANGLAIS: "Anglais",
  ESPAGNOL: "Espagnol",
  ALLEMAND: "Allemand",
  ECONOMIE: "Éco",
  DROIT: "Droit",
  EDUCATION_CIVIQUE: "ECM",
  LITTERATURE: "Littérature",
  EPS: "EPS",
  INFORMATIQUE: "Info",
}

/** Repli sur le libellé complet pour un code qui n'existe pas encore dans cette liste
 * (ex. une matière propre à un pays, seedée ensuite depuis l'admin). */
export function subjectShortLabel(code: string, label: string): string {
  return SUBJECT_SHORT_LABELS[code] ?? label
}
