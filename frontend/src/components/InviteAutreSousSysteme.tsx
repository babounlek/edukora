import { Languages } from "lucide-react"

import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { useCursusListe } from "@/lib/cursusLangue"
import { useI18n } from "@/lib/i18n"
import { langueImposee } from "@/lib/langueProfil"
import { cn } from "@/lib/utils"
import { useChangerLangue } from "@/components/SelecteurLangue"

/**
 * Invite un visiteur à passer dans l'autre sous-système : « Tu prépares le GCE ? » sur la version
 * française, « Tu prépares le BEPC, le Probatoire ou le BAC ? » sur l'anglaise.
 *
 * Les examens proposés suivent la langue de l'interface (voir lib/cursusLangue) : un élève du GCE qui
 * arrive sur la version française ne voit jamais son examen, et le sélecteur FR/EN ne lui dit pas que c'est
 * LUI qui l'y mène. Cette invitation vit aux endroits où l'on choisit son examen.
 *
 * Absente dès qu'un cursus est préparé : la langue est alors celle du cursus (voir langueProfil.ts) et un
 * parent change de sous-système en changeant de profil. Absente aussi quand le pays n'a aucun examen dans
 * l'autre langue (`disponible` faux) : ne jamais promettre un GCE hors du Cameroun.
 *
 * Aucune détection par la langue du navigateur (décision du 2026-10-13) : sur beaucoup de téléphones
 * africains elle est réglée sur l'anglais chez des élèves francophones.
 */
export function InviteAutreSousSysteme({
  disponible,
  variante = "ligne",
  className,
}: {
  /** Le pays a-t-il des examens dans l'autre langue ? */
  disponible: boolean
  /** « ligne » : phrase et lien discrets ; « bloc » : encadré avec bouton, pour une fenêtre. */
  variante?: "ligne" | "bloc"
  className?: string
}) {
  const { t, langue } = useI18n()
  const { user } = useAuth()
  const changerLangue = useChangerLangue()
  if (!disponible || langueImposee(user)) return null

  const cible = langue === "fr" ? "en" : "fr"
  const texte = t(cible === "en" ? "invite_ss.vers_gce" : "invite_ss.vers_francophone")
  const action = t(cible === "en" ? "invite_ss.vers_gce_action" : "invite_ss.vers_francophone_action")

  if (variante === "bloc") {
    return (
      <div className={cn("mt-1 flex flex-col gap-2 rounded-md border border-dashed border-border px-3.5 py-3", className)}>
        <p className="flex items-start gap-2 text-sm text-muted-foreground">
          <Languages className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
          {texte}
        </p>
        <button
          type="button"
          lang={cible}
          onClick={() => void changerLangue(cible)}
          className="min-h-11 self-start rounded-md border border-primary/40 px-3.5 text-sm font-medium text-primary transition-colors hover:bg-primary/5"
        >
          {action}
        </button>
      </div>
    )
  }

  return (
    <p className={cn("text-sm text-muted-foreground", className)}>
      {texte}{" "}
      <button
        type="button"
        lang={cible}
        onClick={() => void changerLangue(cible)}
        className="font-medium text-primary underline-offset-4 hover:underline"
      >
        {action}
      </button>
    </p>
  )
}

/**
 * La même invitation, pour une page qui n'a pas déjà la liste des examens du pays : elle la lit (même clé de
 * cache que partout, voir useCursusListe) pour savoir si l'autre sous-système existe ici.
 */
export function InviteAutreSousSystemeDuPays({ variante, className }: { variante?: "ligne" | "bloc"; className?: string }) {
  const { langue } = useI18n()
  const { country } = useCountry()
  const { tous } = useCursusListe(country, { langue: undefined })
  const disponible = tous.some((c) => c.langue && c.langue !== langue)
  return <InviteAutreSousSysteme disponible={disponible} variante={variante} className={className} />
}
