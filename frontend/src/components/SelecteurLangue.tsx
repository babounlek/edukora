import { useEffect, useRef } from "react"

import { updateMe } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import {
  langueCourante,
  langueDuChemin,
  langueStockee,
  LANGUES,
  memoriserLangue,
  ouvrirDansLangue,
  urlAnglaiseExplicite,
  useI18n,
  type Langue,
} from "@/lib/i18n"
import { langueACharger, langueImposee } from "@/lib/langueProfil"
import { cn } from "@/lib/utils"

/**
 * Accorde la langue de l'interface à l'élève connecté.
 *
 * Avec un cursus préparé, la langue est CELLE DU CURSUS du profil actif (voir langueProfil.ts) : elle ne
 * se choisit pas, elle change avec le profil. La page est rechargée dans cette langue quand elle ne
 * correspond pas ; le choix mémorisé du navigateur la suit, sans quoi le prochain chargement partirait
 * dans l'autre langue. Le compte n'est PAS modifié : sa langue reste celle du parent (messages).
 *
 * Sans cursus préparé, une seule fois par connexion :
 *  - un choix fait sur CE navigateur (avant ou sans connexion) est le plus récent, il part sur le compte ;
 *  - sans choix local, on prend la langue du compte (un élève qui change d'appareil la retrouve) :
 *    l'anglais ouvre la version `/en` de la page, sauf si l'URL a déjà un préfixe de langue - une page
 *    ouverte par un lien `/en/...` reste telle quelle, et ne touche ni au compte ni au choix local.
 * Silencieux en cas d'échec réseau : la langue locale reste, rien ne bloque l'élève.
 */
export function useSynchroLangueCompte() {
  const { user, updateUser } = useAuth()
  const dejaFait = useRef<number | null>(null)
  // Langue imposée vue à l'exécution précédente : undefined tant qu'aucun utilisateur n'a été vu. Sert à
  // reconnaître un CHANGEMENT en cours de session (nouveau cursus, autre profil) plutôt qu'une arrivée.
  const imposeePrecedente = useRef<Langue | null | undefined>(undefined)

  useEffect(() => {
    if (!user) {
      imposeePrecedente.current = undefined
      return
    }
    const imposee = langueImposee(user)
    const precedente = imposeePrecedente.current
    imposeePrecedente.current = imposee
    if (imposee) {
      memoriserLangue(imposee)
      const cible = langueACharger({
        imposee,
        courante: langueCourante(),
        urlExplicite: urlAnglaiseExplicite(),
        changement: precedente !== undefined && precedente !== imposee,
      })
      if (cible) ouvrirDansLangue(cible)
      return
    }
    if (dejaFait.current === user.id) return
    dejaFait.current = user.id
    const locale = langueStockee()
    if (locale) {
      if (locale !== user.langue) updateMe({ langue: locale }).then(updateUser).catch(() => {})
    } else if (user.langue === "en" && langueCourante() === "fr" && !langueDuChemin(window.location.pathname)) {
      memoriserLangue("en")
      ouvrirDansLangue("en")
    }
  }, [user, updateUser])
}

/**
 * Le geste de l'élève qui change de langue (sélecteur, invitation à passer dans l'autre sous-système).
 * Le préfixe d'URL est la base du routeur, fixée au chargement : changer de langue recharge la page sur
 * l'URL de l'autre langue (même page, même requête). Le compte est mis à jour AVANT, sinon le
 * rechargement couperait la requête.
 */
export function useChangerLangue() {
  const { langue } = useI18n()
  const { user, updateUser } = useAuth()
  return async function changerLangue(cible: Langue) {
    if (cible === langue) return
    memoriserLangue(cible)
    if (user && user.langue !== cible) {
      try {
        updateUser(await updateMe({ langue: cible }))
      } catch {
        /* réseau : le choix local suffit, il repartira sur le compte à la prochaine connexion */
      }
    }
    ouvrirDansLangue(cible)
  }
}

/**
 * Bascule français / anglais. Visible partout (barre du haut, menu mobile) : un élève du GCE qui
 * arrive sur une interface en français doit pouvoir en sortir sans la chercher.
 *
 * Absent dès qu'un cursus est préparé : la langue est alors celle du cursus (voir langueProfil.ts), et
 * un parent change de langue en changeant de profil, pas avec ce bouton.
 */
export function SelecteurLangue({ className }: { className?: string }) {
  const { t, langue } = useI18n()
  const { user } = useAuth()
  const choisir = useChangerLangue()
  if (langueImposee(user)) return null

  return (
    <div
      role="group"
      aria-label={t("langue.changer")}
      className={cn("inline-flex h-9 items-center overflow-hidden rounded-md border border-border text-xs font-semibold", className)}
    >
      {LANGUES.map((code) => {
        const actif = code === langue
        return (
          <button
            key={code}
            type="button"
            lang={code}
            aria-pressed={actif}
            aria-label={t(`langue.${code}`)}
            onClick={() => choisir(code)}
            className={cn(
              "h-full px-2.5 uppercase transition-colors",
              actif ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-accent hover:text-foreground",
            )}
          >
            {code}
          </button>
        )
      })}
    </div>
  )
}
