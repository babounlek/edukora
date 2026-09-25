import { useAuth } from "@/context/AuthContext"
import type { CompteARebours, Cursus } from "@/api/types"
import { cn } from "@/lib/utils"

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
  const { user } = useAuth()
  if (!user?.compte_a_rebours || !user.cursus_prepare) return null

  const texte = formatCompteARebours(user.compte_a_rebours)
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
      title={titreDetaille(user.cursus_prepare, user.compte_a_rebours)}
    >
      {formatCursus(user.cursus_prepare)} · {texte}
    </span>
  )
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
  if (compte.estimee) return `vers ${formatMois(compte.date_examen)}`
  if (compte.jours_restants === 0) return "c'est aujourd'hui"
  if (compte.jours_restants === 1) return "demain"
  return `J-${compte.jours_restants}`
}

/** "mai 2028" - à partir de la date AAAA-MM-JJ renvoyée par l'API. */
function formatMois(dateIso: string): string {
  const [annee, mois] = dateIso.split("-").map(Number)
  // `Date` construit en UTC puis formaté en local décalerait d'un mois une date du 1er :
  // on formate à partir des composants, sans jamais passer par un fuseau.
  const nomMois = new Intl.DateTimeFormat("fr-FR", { month: "long" }).format(new Date(annee, mois - 1, 15))
  return `${nomMois} ${annee}`
}

function titreDetaille(cursus: Cursus, compte: CompteARebours): string {
  if (compte.estimee) {
    return `${formatCursus(cursus)} - la date officielle de la prochaine session n'est pas encore publiée, ${compte.session_label} est une estimation.`
  }
  return `${formatCursus(cursus)} - ${compte.session_label}, à partir du ${formatDateComplete(compte.date_examen)}.`
}

/** "24/05/2027". */
function formatDateComplete(dateIso: string): string {
  const [annee, mois, jour] = dateIso.split("-")
  return `${jour}/${mois}/${annee}`
}
