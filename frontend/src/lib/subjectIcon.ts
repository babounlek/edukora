import {
  Atom,
  Beaker,
  BookOpen,
  Brain,
  Code2,
  Dna,
  Dumbbell,
  FlaskConical,
  Globe,
  GraduationCap,
  History,
  Landmark,
  Languages,
  Map,
  PenLine,
  Scale,
  Sigma,
  TrendingUp,
  Wrench,
  type LucideIcon,
} from "lucide-react"

/**
 * Une icône par matière (voir catalog.management.commands.seed_country.SUBJECTS côté
 * backend pour la liste de référence) - repère visuel rapide sur CoursCard/
 * CoursListRow pour scanner une longue liste, en complément du libellé texte déjà
 * affiché (jamais à sa place : l'icône seule ne se comprend pas sans apprentissage).
 * GraduationCap en repli pour un code qui n'existe pas encore dans cette liste (ex.
 * une matière propre à un pays, seedée ensuite depuis l'admin).
 */
const SUBJECT_ICONS: Record<string, LucideIcon> = {
  MATHS: Sigma,
  PHYSIQUE: Atom,
  CHIMIE: FlaskConical,
  PHYSIQUE_CHIMIE: Beaker,
  PHYSIQUE_CHIMIE_TECH: Wrench,
  SVT: Dna,
  FRANCAIS: PenLine,
  PHILOSOPHIE: Brain,
  HISTOIRE: History,
  GEOGRAPHIE: Map,
  HISTOIRE_GEO: Globe,
  ANGLAIS: Languages,
  ESPAGNOL: Languages,
  ALLEMAND: Languages,
  ECONOMIE: TrendingUp,
  DROIT: Scale,
  EDUCATION_CIVIQUE: Landmark,
  LITTERATURE: BookOpen,
  EPS: Dumbbell,
  INFORMATIQUE: Code2,
}

export function subjectIcon(code: string): LucideIcon {
  return SUBJECT_ICONS[code] ?? GraduationCap
}
