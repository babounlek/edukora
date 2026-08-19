import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, Crown, Lock, Sparkles, Unlock } from "lucide-react"

import type { Epreuve } from "@/api/types"
import { formatCursusGroups } from "@/lib/cursus"
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

export function EpreuveCard({ epreuve, className, style, masquerTypeBadge }: EpreuveCardProps) {
  const [titleRef, isTitleTruncated] = useIsTruncated<HTMLHeadingElement>()
  const country = epreuve.subject.country.code.toLowerCase()
  // Une inédite n'a jamais de slug ni de lecteur direct - toujours la fiche détail,
  // qu'il y ait accès ou non (composer crée une tentative, jamais un simple GET).
  const to =
    epreuve.kind === "inedite"
      ? epreuveInediteDetailPath(country, epreuve.slug ?? epreuve.id)
      : epreuve.has_access
        ? epreuveReaderPath(country, epreuve.slug as string)
        : epreuveDetailPath(country, epreuve.slug as string)

  /**
   * Métadonnées secondaires, en une ligne de texte plutôt qu'en pastilles. Composée
   * comme une liste puis jointe : une suite de `<span>·</span>` conditionnels finissait
   * par produire des séparateurs orphelins dès qu'un élément manquait.
   *
   * L'année n'y figure que si le titre ne la porte pas déjà, ou s'il la porte mais que
   * le `line-clamp-2` du titre l'a coupée avant qu'elle soit lisible. Les titres sont
   * composés côté serveur et finissent presque toujours par l'année ("Chimie BAC C et D
   * 2026") : la réafficher juste dessous quand elle est déjà visible se voyait comme un
   * bégaiement - défaut constaté à l'écran, invisible à la lecture du code. D'où la
   * mesure de troncature réelle (isTitleTruncated) plutôt qu'un simple test sur le texte
   * du titre : sur un titre long, l'année est bien dans `epreuve.title` mais coupée par
   * le clamp, donc absente à l'écran - un test textuel seul la masquait à tort.
   */
  const meta: string[] = []
  if (epreuve.year && (isTitleTruncated || !epreuve.title.includes(String(epreuve.year)))) {
    meta.push(String(epreuve.year))
  }
  if (epreuve.nature_epreuve_display) meta.push(epreuve.nature_epreuve_display)
  // origine_display vaut aussi "Épreuve inédite" pour une inédite - déjà porté par le
  // badge couronne, jamais les deux à la fois.
  if (epreuve.kind !== "inedite" && epreuve.origine !== "OFFICIEL") {
    meta.push(
      epreuve.etablissement
        ? `${epreuve.origine_display} - ${epreuve.etablissement}`
        : epreuve.origine_display,
    )
  }

  return (
    <Link to={to} className={className} style={style}>
      <Card
        className={cn(
          "group h-full overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5",
          // Porte le signal "premium" de la bannière promo jusque dans le catalogue
          // fusionné - sans ça, seul le petit badge Couronne distingue une inédite
          // d'un corrigé classique dans une grille dense.
          epreuve.kind === "inedite" && "border-gold/40 hover:border-gold/70 hover:shadow-gold/10",
        )}
      >
        {/* h-full + mt-auto sur le pied : les mentions d'accès s'alignent d'une carte à
            l'autre sur une même ligne de la grille, quelle que soit la longueur du
            titre. */}
        <CardContent className="flex h-full flex-col gap-2 p-4">
          {/* h3 et non h2 : une carte est un élément DANS une section, pas une section.
              En h2, les 24 cartes de la grille d'accueil plus celles des rails
              produisaient 45 titres de même niveau que les 2 vraies sections de la
              page - plan de document inexploitable pour un lecteur d'écran comme
              pour un moteur de recherche. Seul sur sa ligne (le badge de type est
              descendu ci-dessous) : partager la ligne avec un badge lui laissait
              moins de largeur et le faisait tronquer plus tôt, ce qui pouvait couper
              l'année en fin de titre avant qu'elle soit lisible. */}
          <h3 ref={titleRef} className="line-clamp-2 font-display font-medium leading-snug">
            {epreuve.title}
          </h3>
          {/* Le badge de type ouvre la ligne : c'était le plus visible avant (en
              haut à droite), il reste le premier repéré ici. Les autres pastilles -
              gratuit, matière, séries - restent secondaires. L'année, la nature et
              l'origine descendent en pied de carte, en texte. */}
          <div className="flex flex-wrap items-center gap-1.5">
            {!masquerTypeBadge &&
              (epreuve.kind === "inedite" ? (
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
            <Badge variant="secondary">{epreuve.subject.label}</Badge>
            {formatCursusGroups(epreuve.cursus).map((group) => (
              <Badge key={group.key} variant="outline">{group.label}</Badge>
            ))}
          </div>
          {meta.length > 0 && (
            <p className="truncate text-xs text-muted-foreground" title={meta.join(" · ")}>
              {meta.join(" · ")}
            </p>
          )}
          {/* mt-auto : cale la mention d'accès en bas de carte, pour qu'elle s'aligne
              d'une carte à l'autre sur une même ligne quelle que soit la longueur du
              titre ou la présence de la ligne de métadonnées. */}
          <div className="mt-auto flex items-center gap-1.5 text-xs text-muted-foreground">
            {epreuve.est_vitrine ? (
              <>
                <Unlock className="size-3.5 text-success" />
                Corrigé en accès libre
              </>
            ) : epreuve.has_access ? (
              <>
                <Unlock className="size-3.5 text-success" />
                Accès inclus dans ton abonnement
              </>
            ) : (
              <>
                <Lock className="size-3.5" />
                Abonnement requis
              </>
            )}
            {epreuve.is_read && (
              <>
                <span aria-hidden="true">·</span>
                <CheckCircle2 className="size-3.5 text-success" />
                Lu
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
