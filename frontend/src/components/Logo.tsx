import { cn } from "@/lib/utils"
import { langueCourante, useI18n } from "@/lib/i18n"
import { SITE_NAME } from "@/lib/site"
import { DIMENSIONS_LOGO } from "@/lib/brandAssets"

/**
 * - `horizontal` / `vertical` : logo complet avec slogan (français ou anglais selon la langue de l'interface)
 * - `compact` : une seule ligne « EduKora — slogan »
 * - `minimal` : icône + nom, sans slogan (en-têtes, pieds de page : le slogan y serait illisible)
 * - `icon` : le symbole seul
 */
export type VarianteLogo = "horizontal" | "vertical" | "compact" | "minimal" | "icon"

/** `auto` suit le thème de l'app ; `light` / `dark` forcent la version pour fond clair / sombre. */
export type TonLogo = "auto" | "light" | "dark"

const FICHIER: Record<VarianteLogo, string> = {
  horizontal: "logo-horizontal",
  vertical: "logo-vertical",
  compact: "logo-horizontal-compact",
  minimal: "logo-horizontal-minimal",
  icon: "icon",
}
const AVEC_SLOGAN: VarianteLogo[] = ["horizontal", "vertical", "compact"]

interface LogoProps {
  variante?: VarianteLogo
  ton?: TonLogo
  /** Donner la hauteur (ex. `h-9`) ; la largeur suit les proportions du fichier. */
  className?: string
  /** `true` si le nom de la marque est déjà lu à côté (titre, lien déjà nommé) : l'image devient décorative. */
  decoratif?: boolean
}

export function Logo({ variante = "minimal", ton = "auto", className, decoratif = false }: LogoProps) {
  // Se réabonne au changement de langue : le slogan du logo suit la langue de l'interface.
  useI18n()
  const langue = AVEC_SLOGAN.includes(variante) ? `-${langueCourante()}` : ""

  function image(sombre: boolean, classes?: string) {
    const nom = `${FICHIER[variante]}${langue}${sombre ? "-dark" : ""}`
    const [largeur, hauteur] = DIMENSIONS_LOGO[nom]
    return (
      <img
        src={`/brand/${nom}.svg`}
        // Les dimensions du fichier : le navigateur réserve la place avant le chargement (pas de décalage).
        width={largeur}
        height={hauteur}
        alt={decoratif ? "" : SITE_NAME}
        draggable={false}
        className={cn("w-auto max-w-none shrink-0 select-none", className, classes)}
      />
    )
  }

  if (ton === "light") return image(false)
  if (ton === "dark") return image(true)
  return (
    <>
      {image(false, "dark:hidden")}
      {image(true, "hidden dark:block")}
    </>
  )
}
