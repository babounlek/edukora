import { useQuery } from "@tanstack/react-query"

import { listCursus, listEpreuves } from "@/api/endpoints"
import type { Cursus } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { useCursusPrepareEnAttente } from "@/lib/cursusPrepare"
import { estDeLangue, useCursusListe } from "@/lib/cursusLangue"
import { langueCourante } from "@/lib/i18n"

/**
 * L'id du cursus que la personne a déclaré préparer, tel quel (non vérifié contre un pays) :
 * celui de son compte si elle est connectée, sinon celui en attente dans le navigateur.
 */
export function useCursusDeclare(): number | null {
  const { isAuthenticated, user } = useAuth()
  // Toujours appelé, jamais seulement dans la branche "non connecté" : un Hook ne peut
  // pas s'appeler selon une condition qui change d'un rendu à l'autre.
  const enAttente = useCursusPrepareEnAttente()
  return isAuthenticated ? user?.cursus_prepare?.id ?? null : enAttente
}

/**
 * L'examen déclaré, en entier (libellé, série, langue) : celui du compte pour un élève connecté, sinon celui que le visiteur
 * a choisi et que le navigateur garde en attente (voir cursusPrepare.ts), retrouvé dans la liste des examens du pays.
 * Null sans déclaration, ou si l'examen gardé n'est pas de ce pays. `useCursusDeclare` ne rend que l'id : à utiliser quand
 * seul l'id compte. Sans cette lecture, les listes (épreuves, cours, thèmes) ne se pré-filtraient que pour un compte et un
 * visiteur ayant choisi sa série retrouvait tout le catalogue (test élève, 2026-10-19).
 */
export function useCursusPrepareDeclare(country: string | undefined): Cursus | null {
  const { isAuthenticated, user } = useAuth()
  const enAttente = useCursusPrepareEnAttente()
  // La liste n'est demandée que pour un visiteur qui a déclaré quelque chose : même clé de cache que le reste du site.
  const { tous } = useCursusListe(country, { langue: undefined, enabled: !isAuthenticated && enAttente !== null })
  if (isAuthenticated) return user?.cursus_prepare ?? null
  return tous.find((c) => c.id === enAttente) ?? null
}

/**
 * L'examen que prépare la personne qui regarde l'accueil, qu'elle soit connectée
 * (déclaration sur son compte) ou non (déclaration faite à l'onboarding, en attente
 * dans le navigateur - voir cursusPrepare.ts). Null si elle n'a rien déclaré.
 *
 * Toujours vérifié contre les cursus du pays affiché : une déclaration faite sur un
 * autre pays filtrerait l'accueil de /cm sur un cursus sénégalais et le viderait. Même
 * clé de cache que CataloguePage pour la liste des cursus, donc aucune requête en plus.
 *
 * `undefined` tant que cette vérification n'a pas pu se faire (liste pas encore
 * chargée) : répondre `null` d'ici là ferait afficher un instant les inédites de tout
 * le pays avant de les restreindre.
 */
export function useCursusAccueil(country: string): number | null | undefined {
  const { data: cursusList, isError } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
    enabled: Boolean(country),
  })
  const declare = useCursusDeclare()
  if (declare === null) return null
  // Liste indisponible : on retombe sur tout le pays plutôt que de ne rien montrer.
  if (isError) return null
  if (!cursusList) return undefined
  // Un examen déclaré dans l'autre langue que l'interface ne restreint pas l'accueil (voir lib/cursusLangue).
  const examen = cursusList.find((c) => c.id === declare)
  return examen && estDeLangue(examen, langueCourante()) ? declare : null
}

/**
 * Les épreuves inédites mises en avant sur l'accueil : celles du cursus déclaré
 * uniquement - un élève de Probatoire D n'a que faire d'une inédite de BAC C, et la
 * lui présenter en vedette laisse croire que c'est tout ce qu'on a pour lui.
 *
 * Sans cursus déclaré, toutes les inédites du pays, sous la même clé de cache que le
 * Header (qui ne s'en sert que pour savoir s'il en existe au moins une).
 */
export function useInedites(country: string, cursusId: number | null | undefined, enabled = true) {
  // Sans examen choisi, dans la langue de l'interface (l'API l'ignore dès qu'un examen est donné) : en anglais, il
  // n'y a pas encore d'inédite, donc ni vedette ni entrée de menu vers une liste vide.
  const langue = langueCourante()
  return useQuery({
    queryKey: cursusId == null
      ? ["epreuves-inedites-recente", country, langue]
      : ["epreuves-inedites-recente", country, cursusId],
    queryFn: ({ signal }) =>
      listEpreuves({ country, origine: "INEDITE", ordering: "recent", cursus: cursusId ?? undefined, langue }, signal),
    enabled: Boolean(country) && enabled && cursusId !== undefined,
  })
}

/** Lien "toutes les inédites", restreint au même cursus que ce que l'accueil montre -
 * sinon le "Voir les 3 épreuves inédites" ouvrait une liste de 12. */
export function requeteInedites(cursusId: number | null | undefined): string {
  return cursusId == null ? "origine=INEDITE" : `origine=INEDITE&cursus=${cursusId}`
}
