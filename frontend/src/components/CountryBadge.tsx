import { Badge } from "@/components/ui/badge"
import { countryFlagClassName } from "@/lib/countryFlag"

interface CountryBadgeProps {
  code: string
  label: string
}

/**
 * Pays du contenu affiché (pas celui parcouru par ailleurs, voir CountrySwitcher) -
 * un visiteur arrivant par un lien direct doit savoir immédiatement à quel système
 * scolaire ce contenu se rapporte.
 */
export function CountryBadge({ code, label }: CountryBadgeProps) {
  return (
    <Badge variant="outline" className="gap-1.5">
      <span aria-hidden className={countryFlagClassName(code)} />
      {label}
    </Badge>
  )
}
