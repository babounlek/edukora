import { useQuery } from "@tanstack/react-query"

import { listCursus, listEpreuves } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { lireCursusPrepareEnAttente } from "@/lib/cursusPrepare"

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
  const { isAuthenticated, user } = useAuth()
  const { data: cursusList, isError } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
    enabled: Boolean(country),
  })
  const declare = isAuthenticated ? user?.cursus_prepare?.id ?? null : lireCursusPrepareEnAttente()
  if (declare === null) return null
  // Liste indisponible : on retombe sur tout le pays plutôt que de ne rien montrer.
  if (isError) return null
  if (!cursusList) return undefined
  return cursusList.some((c) => c.id === declare) ? declare : null
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
  return useQuery({
    queryKey: cursusId == null
      ? ["epreuves-inedites-recente", country]
      : ["epreuves-inedites-recente", country, cursusId],
    queryFn: ({ signal }) =>
      listEpreuves({ country, origine: "INEDITE", ordering: "recent", cursus: cursusId ?? undefined }, signal),
    enabled: Boolean(country) && enabled && cursusId !== undefined,
  })
}

/** Lien "toutes les inédites", restreint au même cursus que ce que l'accueil montre -
 * sinon le "Voir les 3 épreuves inédites" ouvrait une liste de 12. */
export function requeteInedites(cursusId: number | null | undefined): string {
  return cursusId == null ? "origine=INEDITE" : `origine=INEDITE&cursus=${cursusId}`
}
