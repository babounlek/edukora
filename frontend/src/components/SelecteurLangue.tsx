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
  useI18n,
  type Langue,
} from "@/lib/i18n"
import { cn } from "@/lib/utils"

/**
 * Accorde la langue de l'interface et celle du compte, une fois par connexion :
 *  - un choix fait sur CE navigateur (avant ou sans connexion) est le plus récent, il part sur le compte ;
 *  - sans choix local, on prend la langue du compte (un élève qui change d'appareil la retrouve) :
 *    l'anglais ouvre la version `/en` de la page, sauf si l'URL a déjà un préfixe de langue - une page
 *    ouverte par un lien `/en/...` reste telle quelle, et ne touche ni au compte ni au choix local.
 * Silencieux en cas d'échec réseau : la langue locale reste, rien ne bloque l'élève.
 */
export function useSynchroLangueCompte() {
  const { user, updateUser } = useAuth()
  const dejaFait = useRef<number | null>(null)

  useEffect(() => {
    if (!user || dejaFait.current === user.id) return
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
 * Bascule français / anglais. Visible partout (barre du haut, menu mobile) : un élève du GCE qui
 * arrive sur une interface en français doit pouvoir en sortir sans la chercher.
 */
export function SelecteurLangue({ className }: { className?: string }) {
  const { t, langue } = useI18n()
  const { user, updateUser } = useAuth()

  // Le préfixe d'URL est la base du routeur, fixée au chargement : changer de langue recharge la page
  // sur l'URL de l'autre langue (même page, même requête). Le compte est mis à jour AVANT, sinon le
  // rechargement couperait la requête.
  async function choisir(cible: Langue) {
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
