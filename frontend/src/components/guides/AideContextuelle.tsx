import { useEffect, useId } from "react"
import { CircleHelp, X } from "lucide-react"

import { LivreOuvert } from "@/components/guides/LivreOuvert"
import { Button } from "@/components/ui/button"
import { mettreEnEvidence } from "@/lib/guides/cibles"
import { trouverGuide } from "@/lib/guides/contenu"
import { fermerGuide, lireEtat, memoireActuelle, ouvrirGuide, useEtatGuides } from "@/lib/guides/etat"
import { peutDeclencherAuto } from "@/lib/guides/moteur"
import { useContexteGuide } from "@/lib/guides/useContexte"
import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * Une aide contextuelle, en deux morceaux qui partagent la même définition (contenu.ts) :
 *
 *  - `<AideContextuelle guide="..." />` : la carte, posée dans la page à côté de ce qu'elle
 *    explique. Elle s'affiche seule la PREMIÈRE fois (si le moteur l'autorise, voir
 *    peutDeclencherAuto) et à chaque demande de l'élève. Posée dans le flux de la page, pas
 *    flottante : elle ne masque rien, ne se positionne pas au hasard et s'adapte seule à la
 *    largeur d'un téléphone.
 *  - `<BoutonAide guide="..." />` : le « ? » qui la rouvre, à mettre dans le coin de la page.
 *
 * Les deux n'affichent rien pour un guide inconnu ou qui n'est pas de type « aide ».
 */
export function AideContextuelle({ guide: id, className }: { guide: string; className?: string }) {
  useI18n()
  const guide = trouverGuide(id)
  const etat = useEtatGuides()
  const contexte = useContexteGuide()
  const titreId = useId()
  const ouvertIci = etat.ouvert?.id === id

  // Première apparition automatique. Se relance quand la situation change (identité lue, écran
  // d'accueil du compte fermé...) ; le moteur refuse tant qu'une règle l'interdit.
  const { identite, ouvert, autoDejaMontre, revision } = etat
  useEffect(() => {
    if (!guide || guide.type !== "aide" || !identite) return
    const situation = { memoire: memoireActuelle(), guideOuvert: ouvert !== null, autoDejaMontre }
    if (peutDeclencherAuto(guide, contexte(), situation)) ouvrirGuide(id, { explicite: false })
  }, [guide, id, identite, ouvert, autoDejaMontre, revision, contexte])

  const cible = guide?.etapes[0]?.cible
  useEffect(() => {
    if (!ouvertIci || !lireEtat().ouvert?.explicite) return
    return mettreEnEvidence(cible)
  }, [ouvertIci, cible])

  if (!guide || guide.type !== "aide" || !ouvertIci) return null
  const explicite = etat.ouvert?.explicite ?? false

  return (
    <section
      aria-labelledby={titreId}
      className={cn("animate-fade-up mt-4 rounded-xl border border-primary/30 bg-accent/60 p-4", className)}
    >
      <div className="flex items-start gap-3">
        <LivreOuvert className="mt-0.5 text-primary" />
        <div className="min-w-0 flex-1">
          <h3 id={titreId} className="font-display text-base font-semibold leading-snug">
            {t(guide.titre)}
          </h3>
          <ul className="mt-1.5 space-y-1.5 text-sm leading-relaxed text-muted-foreground">
            {guide.etapes.map((etape) => (
              <li key={etape.id}>{t(etape.texte)}</li>
            ))}
          </ul>
        </div>
        <button
          type="button"
          onClick={() => fermerGuide(explicite ? undefined : "ignore")}
          aria-label={t("guide.fermer")}
          className="-mr-1 -mt-1 flex size-11 shrink-0 items-center justify-center rounded-full text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/50"
        >
          <X className="size-4" />
        </button>
      </div>
      <div className="mt-3 flex justify-end">
        <Button type="button" variant="outline" className="min-h-11" onClick={() => fermerGuide("termine")}>
          {t("guide.compris")}
        </Button>
      </div>
    </section>
  )
}

export function BoutonAide({ guide: id, className }: { guide: string; className?: string }) {
  useI18n()
  const guide = trouverGuide(id)
  const { ouvert } = useEtatGuides()
  // Pas de « ? » quand l'aide est déjà sous les yeux, ni sans identité (rien à rouvrir pour personne).
  if (!guide || guide.type !== "aide" || ouvert?.id === id) return null
  return (
    <button
      type="button"
      onClick={() => ouvrirGuide(id, { explicite: true })}
      className={cn(
        "inline-flex min-h-11 items-center gap-1.5 rounded-full px-2.5 text-xs font-medium text-muted-foreground outline-none transition-colors hover:bg-accent hover:text-foreground focus-visible:ring-2 focus-visible:ring-ring/50 sm:min-h-9",
        className,
      )}
    >
      <CircleHelp className="size-4" aria-hidden="true" />
      <span>{t("guide.aide.rappel")}</span>
    </button>
  )
}
