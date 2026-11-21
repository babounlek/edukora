import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { ArrowRight } from "lucide-react"

import { usePremiereSeance } from "@/components/PremiereSeance"
import { Button } from "@/components/ui/button"
import { trackEvent } from "@/lib/analytics"
import { libelleCursus } from "@/lib/cursus"
import { t, useI18n } from "@/lib/i18n"
import { capitaliserTheme } from "@/lib/utils"

/** Les repères que la barre observe : la carte du hero (voir PremiereSeance) et la fin de la vitrine (voir CataloguePage). */
const SELECTEUR_CARTE = '[data-guide="premiere-seance"]'
const SELECTEUR_FIN = "[data-fin-vitrine], footer"

/**
 * La carte du hero est-elle passée au-dessus de l'écran, sans que la fin de page soit encore là ? Vrai seulement entre
 * les deux : la barre ne double jamais la carte qu'on a sous les yeux, et ne recouvre ni le dernier bloc (« Voir les
 * prix ») ni le pied de page. Faux sans IntersectionObserver.
 */
function useEntreCarteEtFin(): boolean {
  const [carteDepassee, setCarteDepassee] = useState(false)
  const [finVisible, setFinVisible] = useState(false)

  useEffect(() => {
    if (typeof IntersectionObserver === "undefined") return
    const carte = document.querySelector(SELECTEUR_CARTE)
    if (!carte) return
    const fins = new Set<Element>()
    const observateur = new IntersectionObserver((entrees) => {
      for (const entree of entrees) {
        if (entree.target === carte) {
          // Hors de l'écran ET au-dessus : sous l'écran (page pas encore défilée), la carte est encore à venir.
          setCarteDepassee(!entree.isIntersecting && entree.boundingClientRect.bottom <= 0)
        } else {
          if (entree.isIntersecting) fins.add(entree.target)
          else fins.delete(entree.target)
          setFinVisible(fins.size > 0)
        }
      }
    })
    observateur.observe(carte)
    document.querySelectorAll(SELECTEUR_FIN).forEach((element) => observateur.observe(element))
    return () => observateur.disconnect()
  }, [])

  return carteDepassee && !finVisible
}

/**
 * La barre « Commencer » du visiteur, sur un téléphone : collée en bas de l'écran une fois la carte du hero dépassée.
 *
 * Entre cette carte et « Voir les prix », la vitrine faisait défiler cinq écrans sans un seul bouton pour commencer
 * (audit des accueils, 2026-11-21, V3) : le visiteur convaincu par l'extrait de corrigé devait remonter. Elle porte la
 * même action que la carte, et rien d'autre : l'examen choisi, le thème, « Commencer ». Sans examen choisi, elle ramène
 * à la question « Tu prépares quel examen ? ». Toutes les séances gratuites jouées : elle mène aux abonnements.
 *
 * Seulement sous `md` : sur un écran large la carte reste visible longtemps et l'en-tête porte déjà « Prix ».
 */
export function BarreCommencer({ country }: { country: string }) {
  useI18n()
  const visible = useEntreCarteEtFin()
  const { choisi, essaisEnAttente, essai, total, lancement, commencer } = usePremiereSeance(country, "barre_commencer")
  // Rien à proposer (examen sans séance gratuite) : pas de barre vide.
  if (!visible || essaisEnAttente || (choisi && !essai && total === 0)) return null

  const remonter = () => {
    trackEvent("accueil_bouton_clic", { cible: "barre_examen" })
    document.querySelector(SELECTEUR_CARTE)?.scrollIntoView({ block: "center" })
  }

  return (
    <div
      role="region"
      aria-label={t("barre.aria")}
      className="fixed inset-x-0 bottom-0 z-30 border-t border-border bg-background/95 px-4 py-2.5 pb-[calc(0.625rem+env(safe-area-inset-bottom))] shadow-[0_-4px_16px_rgb(0_0_0/0.06)] backdrop-blur md:hidden"
    >
      {!choisi ? (
        <Button className="min-h-11 w-full" onClick={remonter}>
          {t("barre.choisir_examen")}
        </Button>
      ) : essai ? (
        <div className="flex items-center gap-3">
          <p className="min-w-0 flex-1 leading-tight">
            <span className="block truncate text-xs text-muted-foreground">{libelleCursus(choisi)} · {essai.subject_label}</span>
            <span className="block truncate text-sm font-semibold">{capitaliserTheme(essai.theme_name)}</span>
          </p>
          <Button className="min-h-11 shrink-0" disabled={lancement} onClick={() => commencer(essai)}>
            {/* « Commencer » tout court : « sans compte » est dit par la carte, et le thème doit rester lisible à 375 px. */}
            {lancement ? t("quiz.preparation") : t("premiere.commencer")}
            {!lancement && <ArrowRight />}
          </Button>
        </div>
      ) : total > 0 ? (
        <Button asChild className="min-h-11 w-full">
          <Link to="/tarifs" onClick={() => trackEvent("accueil_bouton_clic", { cible: "prix" })}>
            {t("essai.voir_abonnements")}
            <ArrowRight />
          </Link>
        </Button>
      ) : null}
    </div>
  )
}
