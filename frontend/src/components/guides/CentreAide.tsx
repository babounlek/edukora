import { useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { Check } from "lucide-react"

import { LivreOuvert } from "@/components/guides/LivreOuvert"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetDescription, SheetTitle } from "@/components/ui/sheet"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { GUIDES, guideDeBienvenue } from "@/lib/guides/contenu"
import {
  fermerCentre, ouvrirGuide, reglerAidesAuto, toutRevoir, useGuides,
} from "@/lib/guides/etat"
import { estAJour } from "@/lib/guides/store"
import type { DefinitionGuide } from "@/lib/guides/types"
import { catalogueHomePath } from "@/lib/countryPath"
import { t, useI18n } from "@/lib/i18n"

/**
 * Le centre d'aide : tous les guides au même endroit, à relire ou à relancer, sans repasser
 * par le parcours de bienvenue. Un panneau (comme le menu du Header) plutôt qu'une page :
 * il s'ouvre depuis n'importe où sans quitter ce que l'élève est en train de lire, et il
 * n'ajoute ni route ni segment d'URL à traduire.
 *
 * Il liste les MÊMES définitions que le tutoriel et les aides de page (lib/guides/contenu.ts) :
 * les textes ne sont écrits qu'une fois.
 */
export function CentreAide() {
  useI18n()
  const { centreOuvert, memoire } = useGuides()
  const { isAuthenticated } = useAuth()
  const { country } = useCountry()
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const [revoir, setRevoir] = useState(false)

  // Ce que ce lecteur peut relancer : la bienvenue qui lui correspond, et les aides de page qui
  // existent pour un élève (un visiteur n'a pas de séance du jour à qui expliquer quoi que ce soit).
  const guides: DefinitionGuide[] = [
    guideDeBienvenue(isAuthenticated),
    ...GUIDES.filter((guide) => guide.type === "aide" && (isAuthenticated || guide.public === "visiteur")),
  ]

  function relancer(guide: DefinitionGuide) {
    fermerCentre()
    // Un guide ne se déroule qu'à sa page : on y emmène l'élève d'abord. Le changement de page
    // ne le ferme pas, puisqu'une page où il a un sens est précisément celle où l'on arrive.
    ouvrirGuide(guide.id, { explicite: true })
    if (!guide.route(pathname)) navigate(catalogueHomePath(country))
  }

  return (
    <Sheet open={centreOuvert} onOpenChange={(ouvert) => !ouvert && fermerCentre()}>
      <SheetContent className="overflow-y-auto">
        <SheetTitle className="flex items-center gap-2">
          <LivreOuvert className="text-primary" />
          {t("guide.centre.titre")}
        </SheetTitle>
        <SheetDescription>{t("guide.centre.description")}</SheetDescription>

        <ul className="mt-5 space-y-4">
          {guides.map((guide) => (
            <li key={guide.id} className="rounded-xl border border-border bg-card p-4">
              <div className="flex items-start justify-between gap-3">
                <h3 className="font-display text-base font-semibold leading-snug">{t(guide.titre)}</h3>
                {estAJour(memoire, guide.id, guide.version) && (
                  <span className="inline-flex shrink-0 items-center gap-1 text-xs text-muted-foreground">
                    <Check className="size-3.5" aria-hidden="true" />
                    {t("guide.centre.vu")}
                  </span>
                )}
              </div>
              <p className="mt-1 text-sm text-muted-foreground">{t(guide.description)}</p>
              {/* Les explications elles-mêmes, lisibles sans relancer quoi que ce soit. */}
              <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm leading-relaxed">
                {guide.etapes.map((etape) => (
                  <li key={etape.id}>
                    <span className="font-medium">{t(etape.titre)}</span>
                    <span className="block text-muted-foreground">{t(etape.texte)}</span>
                  </li>
                ))}
              </ol>
              <Button type="button" variant="outline" className="mt-4 min-h-11 w-full" onClick={() => relancer(guide)}>
                {t("guide.centre.relancer")}
              </Button>
            </li>
          ))}
        </ul>

        <div className="mt-6 space-y-3 border-t border-border pt-4">
          <label className="flex min-h-11 items-start gap-3 text-sm">
            <input
              type="checkbox"
              checked={memoire.prefs.aidesAuto}
              onChange={(evenement) => reglerAidesAuto(evenement.target.checked)}
              className="mt-0.5 size-5 shrink-0 accent-primary"
            />
            <span>
              <span className="block font-medium">{t("guide.centre.auto")}</span>
              <span className="block text-muted-foreground">{t("guide.centre.auto_aide")}</span>
            </span>
          </label>
          <Button
            type="button"
            variant="ghost"
            className="min-h-11 px-3 text-muted-foreground"
            onClick={() => {
              toutRevoir()
              setRevoir(true)
            }}
          >
            {t("guide.centre.tout_revoir")}
          </Button>
          <p aria-live="polite" className="text-sm text-muted-foreground">
            {revoir ? t("guide.centre.tout_revoir_fait") : ""}
          </p>
          <p className="text-xs text-muted-foreground">{t("guide.centre.local")}</p>
        </div>
      </SheetContent>
    </Sheet>
  )
}
