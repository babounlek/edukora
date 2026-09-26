import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { ArrowRight, CheckCircle2, Clock, Crown, Eye, FileText, Sparkles, Unlock } from "lucide-react"

import type { Epreuve } from "@/api/types"
import { formatCursusGroups } from "@/lib/cursus"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { epreuveDetailPath, epreuveInediteDetailPath, epreuveReaderPath } from "@/lib/countryPath"
import { useIsTruncated } from "@/lib/useIsTruncated"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

interface EpreuveCardProps {
  epreuve: Epreuve
  className?: string
  style?: CSSProperties
  /**
   * Masque le badge de type, pour un contexte qui l'annonce déjà (le rail "Épreuves
   * Inédites", dont les douze cartes le répétaient à l'identique). Jamais dans la
   * grille fusionnée du catalogue, où ce badge est le seul moyen de repérer une
   * inédite parmi trois cent quarante-deux épreuves.
   */
  masquerTypeBadge?: boolean
}

/** "3 h" pour un classique (texte saisi à la transcription), "90 min" pour une inédite
 * (Blueprint.duree_minutes) - jamais les deux, jamais une durée inventée. */
function dureeAffichee(epreuve: Epreuve): string | null {
  if (epreuve.duree_epreuve) return epreuve.duree_epreuve
  if (epreuve.duree_minutes) return `${epreuve.duree_minutes} min`
  return null
}

export function EpreuveCard({ epreuve, className, style, masquerTypeBadge }: EpreuveCardProps) {
  const [titleRef, isTitleTruncated] = useIsTruncated<HTMLHeadingElement>()
  const country = epreuve.subject.country.code.toLowerCase()
  const inedite = epreuve.kind === "inedite"
  // Une inédite n'a jamais de slug ni de lecteur direct - toujours la fiche détail,
  // qu'il y ait accès ou non (composer crée une tentative, jamais un simple GET).
  const to = inedite
    ? epreuveInediteDetailPath(country, epreuve.slug ?? epreuve.id)
    : epreuve.has_access
      ? epreuveReaderPath(country, epreuve.slug as string)
      : epreuveDetailPath(country, epreuve.slug as string)

  const Icone = subjectIcon(epreuve.subject.code)
  const couleur = couleurMatiere(epreuve.subject.code)
  const duree = dureeAffichee(epreuve)

  /**
   * Métadonnées secondaires. L'année n'y figure que si le titre ne la porte pas déjà, ou
   * s'il la porte mais que le `line-clamp-2` l'a coupée avant qu'elle soit lisible : les
   * titres sont composés côté serveur et finissent presque toujours par l'année, la
   * réafficher quand elle est déjà visible se voyait comme un bégaiement (d'où la mesure
   * de troncature réelle, isTitleTruncated, plutôt qu'un test textuel seul).
   */
  const faits: { icone: typeof Clock; texte: string }[] = []
  if (epreuve.year && (isTitleTruncated || !epreuve.title.includes(String(epreuve.year)))) {
    faits.push({ icone: Clock, texte: `Session ${epreuve.year}` })
  }
  if (epreuve.exercises_count > 0) {
    faits.push({
      icone: FileText,
      texte: `${epreuve.exercises_count} exercice${epreuve.exercises_count > 1 ? "s" : ""}`,
    })
  }
  if (duree) faits.push({ icone: Clock, texte: duree })
  if (/^\d+([.,]\d+)?$/.test(epreuve.coefficient.trim())) {
    faits.push({ icone: Sparkles, texte: `Coef. ${epreuve.coefficient.trim()}` })
  }

  // origine_display vaut aussi "Épreuve inédite" pour une inédite - déjà porté par le
  // badge couronne, jamais les deux à la fois.
  const provenance =
    !inedite && epreuve.origine !== "OFFICIEL"
      ? epreuve.etablissement
        ? `${epreuve.origine_display} - ${epreuve.etablissement}`
        : epreuve.origine_display
      : null

  return (
    <Link to={to} className={cn("group block h-full rounded-xl focus-visible:outline-none", className)} style={style}>
      <Card
        className={cn(
          "relative h-full overflow-hidden transition-all duration-300 group-hover:-translate-y-1 group-hover:border-primary/50 group-hover:shadow-lg group-hover:shadow-primary/[0.07] group-focus-visible:ring-2 group-focus-visible:ring-ring",
          // Porte le signal "premium" de la bannière promo jusque dans le catalogue
          // fusionné - sans ça, seul le petit badge Couronne distingue une inédite
          // d'un corrigé classique dans une grille dense.
          inedite && "border-gold/40 group-hover:border-gold/70 group-hover:shadow-gold/10",
        )}
      >
        {/* Filet de matière : repère de couleur d'un coup d'œil dans une grille de 24
            cartes, avant même de lire un titre. Or pour une inédite (signal premium). */}
        <div aria-hidden className={cn("h-1 w-full", inedite ? "bg-gradient-to-r from-gold to-gold/40" : couleur.barre)} />
        <CardContent className="flex h-[calc(100%-0.25rem)] flex-col gap-3 p-4">
          <div className="flex items-start gap-3">
            <span className={cn("flex size-10 shrink-0 items-center justify-center rounded-xl", couleur.puce)}>
              <Icone className="size-5" aria-hidden="true" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-medium uppercase tracking-wide text-muted-foreground">
                {epreuve.subject.label}
              </p>
              {/* h3 et non h2 : une carte est un élément DANS une section, pas une section
                  (45 titres de même niveau que les vraies sections rendraient le plan du
                  document inexploitable pour un lecteur d'écran comme pour un moteur de
                  recherche). Seul sur sa ligne : partager avec un badge le ferait tronquer
                  plus tôt et pourrait couper l'année avant qu'elle soit lisible. */}
              <h3 ref={titleRef} className="mt-0.5 line-clamp-2 font-display text-base font-medium leading-snug">
                {epreuve.title}
              </h3>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-1.5">
            {!masquerTypeBadge &&
              (inedite ? (
                <Badge variant="gold" className="gap-1">
                  <Crown className="size-3" />
                  Épreuve inédite
                </Badge>
              ) : (
                <Badge variant={epreuve.lesson_type === "SUJET" ? "gold" : "outline"}>
                  {epreuve.lesson_type_display}
                </Badge>
              ))}
            {epreuve.est_vitrine && (
              <Badge variant="success" className="gap-1">
                <Sparkles className="size-3" />
                Gratuit
              </Badge>
            )}
            {formatCursusGroups(epreuve.cursus).map((group) => (
              <Badge key={group.key} variant="secondary">{group.label}</Badge>
            ))}
          </div>

          {(faits.length > 0 || provenance) && (
            <div className="flex flex-col gap-1 text-sm text-muted-foreground">
              {faits.length > 0 && (
                <p className="flex flex-wrap items-center gap-x-3 gap-y-1">
                  {faits.map(({ icone: IconeFait, texte }) => (
                    <span key={texte} className="inline-flex items-center gap-1">
                      <IconeFait className="size-3.5 shrink-0" aria-hidden="true" />
                      {texte}
                    </span>
                  ))}
                </p>
              )}
              {provenance && <p className="truncate" title={provenance}>{provenance}</p>}
            </div>
          )}

          {/* Le pied dit CE QUE LE CLIC FAIT, pas ce qu'on n'a pas : "Abonnement requis"
              écartait avant même d'avoir vu, alors qu'un aperçu gratuit existe. mt-auto :
              l'action s'aligne d'une carte à l'autre quelle que soit la hauteur du contenu. */}
          <div className="mt-auto flex items-center justify-between gap-2 border-t border-border/70 pt-3 text-sm">
            <span className="flex min-w-0 items-center gap-1.5">
              {epreuve.est_vitrine || epreuve.has_access ? (
                <>
                  <Unlock className="size-4 shrink-0 text-success" aria-hidden="true" />
                  <span className="truncate font-medium text-foreground">
                    {inedite ? "Composer l'épreuve" : epreuve.est_vitrine ? "Lire - accès libre" : "Lire le corrigé"}
                  </span>
                </>
              ) : (
                <>
                  <Eye className="size-4 shrink-0 text-primary" aria-hidden="true" />
                  <span className="truncate font-medium text-foreground">Voir l'aperçu</span>
                </>
              )}
              {epreuve.is_read && (
                <span className="inline-flex shrink-0 items-center gap-1 text-success">
                  <CheckCircle2 className="size-3.5" aria-hidden="true" />
                  Lu
                </span>
              )}
            </span>
            <ArrowRight
              className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-1"
              aria-hidden="true"
            />
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
