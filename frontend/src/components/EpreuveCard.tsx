import type { CSSProperties } from "react"
import { Link } from "react-router-dom"
import { CheckCircle2, Crown, Lock, Sparkles, Unlock } from "lucide-react"

import type { Epreuve } from "@/api/types"
import { formatCursusGroups } from "@/lib/cursus"
import { epreuveDetailPath, epreuveInediteDetailPath, epreuveReaderPath } from "@/lib/countryPath"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"

interface EpreuveCardProps {
  epreuve: Epreuve
  className?: string
  style?: CSSProperties
}

export function EpreuveCard({ epreuve, className, style }: EpreuveCardProps) {
  const country = epreuve.subject.country.code.toLowerCase()
  // Une inédite n'a jamais de slug ni de lecteur direct - toujours la fiche détail,
  // qu'il y ait accès ou non (composer crée une tentative, jamais un simple GET).
  const to =
    epreuve.kind === "inedite"
      ? epreuveInediteDetailPath(country, epreuve.slug ?? epreuve.id)
      : epreuve.has_access
        ? epreuveReaderPath(country, epreuve.slug as string)
        : epreuveDetailPath(country, epreuve.slug as string)
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
        <CardContent className="flex flex-col gap-2 p-4">
          <div className="flex items-start justify-between gap-2">
            <h2 className="line-clamp-2 font-display font-medium leading-snug">
              {epreuve.title}
            </h2>
            {epreuve.kind === "inedite" ? (
              <Badge variant="gold" className="shrink-0 gap-1">
                <Crown className="size-3" />
                Épreuve inédite
              </Badge>
            ) : (
              <Badge variant={epreuve.lesson_type === "SUJET" ? "gold" : "outline"} className="shrink-0">
                {epreuve.lesson_type_display}
              </Badge>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {epreuve.est_vitrine && (
              <Badge variant="success" className="gap-1">
                <Sparkles className="size-3" />
                Gratuit
              </Badge>
            )}
            <Badge variant="secondary">{epreuve.subject.label}</Badge>
            {epreuve.nature_epreuve_display && (
              <Badge variant="outline">{epreuve.nature_epreuve_display}</Badge>
            )}
            {formatCursusGroups(epreuve.cursus).map((group) => (
              <Badge key={group.key} variant="outline">{group.label}</Badge>
            ))}
            {epreuve.year && <Badge variant="outline">{epreuve.year}</Badge>}
            {/* Le badge origine ci-dessous affiche aussi "Épreuve inédite" pour une
                inédite (origine_display) - déjà porté par le badge couronne ci-dessus,
                jamais les deux à la fois. */}
            {epreuve.kind !== "inedite" && epreuve.origine !== "OFFICIEL" && (
              <Badge variant="outline">
                {epreuve.origine_display}
                {epreuve.etablissement ? ` - ${epreuve.etablissement}` : ""}
              </Badge>
            )}
          </div>
          <div className="mt-1 flex items-center gap-1.5 text-xs text-muted-foreground">
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
