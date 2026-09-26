import { Check, CircleDashed, CircleDot, RotateCcw, type LucideIcon } from "lucide-react"

/**
 * La langue de la progression : quatre statuts, chacun avec UNE couleur et UNE icône, partagées
 * par les barres, les compteurs, la légende, les badges et la frise des savoirs.
 *
 * Règles qui tiennent l'ensemble :
 * - la couleur d'un STATUT n'est jamais utilisée pour autre chose sur ces écrans, et celle d'une
 *   MATIÈRE (voir matiereCouleur) ne colore jamais une barre : sinon le bleu ciel des maths se
 *   lirait "en cours" et l'orange de la physique "en révision" ;
 * - l'icône double toujours la couleur : quelqu'un qui ne distingue pas le vert de l'orange, ou
 *   qui lit au soleil sur un écran d'entrée de gamme, lit encore le statut ;
 * - le doré n'est PAS "en révision" (c'est le signal "ce qui tombe à l'examen" et les paliers) :
 *   l'ambre orangé du token `warning` porte les révisions.
 */
export type StatutProgression = "maitrise" | "en_revision" | "en_cours" | "a_decouvrir"

export interface StyleStatut {
  libelle: string
  Icone: LucideIcon
  /** Fond doux + texte : pastille d'icône et badge. */
  puce: string
  /** Aplat plein : segment de barre. */
  barre: string
}

export const STATUTS: Record<StatutProgression, StyleStatut> = {
  maitrise: {
    libelle: "Maîtrisé",
    Icone: Check,
    puce: "bg-primary/10 text-primary",
    barre: "bg-primary",
  },
  en_revision: {
    libelle: "En révision",
    Icone: RotateCcw,
    puce: "bg-warning/15 text-warning-foreground dark:text-warning",
    barre: "bg-warning",
  },
  en_cours: {
    libelle: "En cours",
    Icone: CircleDot,
    puce: "bg-info/15 text-info",
    barre: "bg-info",
  },
  a_decouvrir: {
    libelle: "À découvrir",
    Icone: CircleDashed,
    puce: "bg-muted text-muted-foreground",
    barre: "bg-muted ring-1 ring-border",
  },
}
