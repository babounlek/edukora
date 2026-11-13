import { useQuery } from "@tanstack/react-query"

import { getCompteAReboursCursus } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import type { CompteARebours, Cursus } from "@/api/types"
import { useCursusPrepareDeclare } from "@/lib/cursusAccueil"
import { cn } from "@/lib/utils"
import { localeCourante, t, useI18n } from "@/lib/i18n"

/**
 * "BAC D · J-244" - le compte à rebours jusqu'à l'examen préparé.
 *
 * Volontairement neutre : gris, jamais de rouge, jamais de clignotement, même à
 * quelques jours de l'épreuve. L'angoisse d'examen ne manque pas à nos élèves, c'est
 * un ordre de marche qui leur manque - un décompte alarmiste ferait fermer l'onglet
 * au moment précis où il faudrait l'ouvrir.
 *
 * Silencieusement absent (pas de message, pas de place réservée) tant qu'aucun cursus
 * n'est déclaré ou qu'aucune session d'examen n'est saisie pour ce diplôme : c'est un
 * repère offert, jamais une information qu'on réclame.
 */
export function CompteAReboursBadge({
  className,
  variant = "texte",
}: {
  className?: string
  variant?: "texte" | "pilule"
}) {
  // Abonne le badge au changement de langue : formatCompteARebours lit la langue courante.
  useI18n()
  const decompte = useCompteARebours()
  if (!decompte) return null

  const texte = formatCompteARebours(decompte.compte)
  if (!texte) return null

  return (
    <span
      className={cn(
        "font-medium tabular-nums",
        // La pastille sert au bandeau du haut et à la barre du bas : lisible d'un coup
        // d'œil, mais toujours neutre (jamais de rouge, voir plus haut).
        variant === "pilule"
          ? "rounded-full border border-border bg-muted/60 px-2.5 py-1 text-xs font-semibold text-foreground"
          : "text-xs text-muted-foreground",
        className,
      )}
      title={titreDetaille(decompte.cursus, decompte.compte)}
    >
      {/* Un visiteur a déjà son examen dans la pastille juste à côté (PastilleExamen) : on ne le répète pas. */}
      {decompte.visiteur ? texte : `${formatCursus(decompte.cursus)} · ${texte}`}
    </span>
  )
}

/**
 * Le décompte à afficher pour qui regarde le site, avec l'examen auquel il se rapporte : celui du compte pour un élève connecté
 * (reçu avec `getMe`), sinon celui du visiteur qui a choisi son examen sans compte (demandé au serveur : la même date, estimée ou
 * non). Null tant qu'aucun examen n'est déclaré, qu'aucune session n'est saisie, ou que la réponse n'est pas là : un repère offert,
 * jamais un manque.
 */
export function useCompteARebours(): { cursus: Cursus; compte: CompteARebours; visiteur: boolean } | null {
  const { isAuthenticated, user } = useAuth()
  const { country } = useCountry()
  // Toujours appelés, jamais selon la connexion : un Hook ne s'appelle pas sous condition. Pour un compte, la liste des
  // examens n'est pas demandée (voir useCursusPrepareDeclare) et la requête ci-dessous reste coupée.
  const declare = useCursusPrepareDeclare(country)
  const { data } = useQuery({
    queryKey: ["compte-a-rebours", declare?.id ?? null],
    queryFn: ({ signal }) => getCompteAReboursCursus(declare!.id, signal),
    enabled: !isAuthenticated && declare !== null,
    staleTime: 60 * 60_000,
  })
  if (isAuthenticated) {
    return user?.compte_a_rebours && user.cursus_prepare
      ? { cursus: user.cursus_prepare, compte: user.compte_a_rebours, visiteur: false }
      : null
  }
  return declare && data ? { cursus: declare, compte: data, visiteur: true } : null
}

/** "BAC D", "BEPC" - le diplôme, et la série seulement quand il y en a une. */
export function formatCursus(cursus: Cursus): string {
  return cursus.series ? `${cursus.examen_display} ${cursus.series.code}` : cursus.examen_display
}

/**
 * "J-244" quand la date officielle est connue, "vers mai 2028" quand elle est
 * seulement estimée : afficher "J-613" sur une date qu'on a nous-mêmes décalée d'un
 * an serait une précision inventée (voir ExamSession.compte_a_rebours_pour).
 *
 * Renvoie une chaîne vide pour un décompte négatif - l'examen est passé et la session
 * suivante n'est pas encore saisie ; il n'y a alors rien d'honnête à afficher.
 */
export function formatCompteARebours(compte: CompteARebours): string {
  if (compte.jours_restants < 0) return ""
  if (compte.estimee) return t("compte_a_rebours.vers", { mois: formatMois(compte.date_examen) })
  if (compte.jours_restants === 0) return t("compte_a_rebours.aujourdhui")
  if (compte.jours_restants === 1) return t("compte_a_rebours.demain")
  return t("compte_a_rebours.jours", { n: compte.jours_restants })
}

/** "mai 2028" - à partir de la date AAAA-MM-JJ renvoyée par l'API. */
function formatMois(dateIso: string): string {
  const [annee, mois] = dateIso.split("-").map(Number)
  // `Date` construit en UTC puis formaté en local décalerait d'un mois une date du 1er :
  // on formate à partir des composants, sans jamais passer par un fuseau.
  const nomMois = new Intl.DateTimeFormat(localeCourante(), { month: "long" }).format(new Date(annee, mois - 1, 15))
  return `${nomMois} ${annee}`
}

function titreDetaille(cursus: Cursus, compte: CompteARebours): string {
  const variables = { cursus: formatCursus(cursus), session: compte.session_label }
  if (compte.estimee) return t("compte_a_rebours.titre_estime", variables)
  return t("compte_a_rebours.titre_exact", { ...variables, date: formatDateComplete(compte.date_examen) })
}

/** "24/05/2027". */
function formatDateComplete(dateIso: string): string {
  const [annee, mois, jour] = dateIso.split("-")
  return `${jour}/${mois}/${annee}`
}
