import { Badge } from "@/components/ui/badge"
import { countryFlagClassName } from "@/lib/countryFlag"
import { useI18n } from "@/lib/i18n"
import { libellePays } from "@/lib/pays"

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
  useI18n()
  return (
    <Badge variant="outline" className="gap-1.5">
      <span aria-hidden className={countryFlagClassName(code)} />
      {libellePays(code, label)}
    </Badge>
  )
}
