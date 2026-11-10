import { Check, Minus } from "lucide-react"

import { t } from "@/lib/i18n"
import { SITE_NAME } from "@/lib/site"

/**
 * Comparatif "plateforme vs fascicule de corrigés" pour /tarifs (2026-11-10).
 *
 * Le parent compare spontanément nos 15 000 FCFA à un fascicule de corrigés PDF
 * vendu quelques milliers de francs : on lui montre donc ce qu'un document figé ne
 * fait pas. Chaque ligne de gauche correspond à une fonction réelle de la
 * plateforme (déjà listée dans les puces "Tout ce dont tu as besoin"), jamais à un
 * argument de copywriting. Colonne de droite : un fascicule "type", sans nommer de
 * concurrent ni lui prêter de défaut qu'on n'a pas vérifié - d'où "rarement" plutôt
 * que "non" quand un fascicule peut en contenir un équivalent partiel.
 */
type Valeur = "oui" | "non" | "rarement"

interface Ligne {
  cle: string
  fascicule: Valeur
}

const LIGNES: Ligne[] = [
  { cle: "corriges", fascicule: "oui" },
  { cle: "cours", fascicule: "rarement" },
  { cle: "quiz", fascicule: "non" },
  { cle: "themes", fascicule: "rarement" },
  { cle: "suivi", fascicule: "non" },
  { cle: "maj", fascicule: "non" },
]

function Cellule({ valeur }: { valeur: Valeur }) {
  if (valeur === "oui") {
    return (
      <span className="inline-flex items-center gap-1.5">
        <Check className="size-4 text-success" aria-hidden />
        <span className="sr-only">{t("comparatif.oui")}</span>
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1.5 text-muted-foreground">
      <Minus className="size-4" aria-hidden />
      <span className="text-xs">
        {valeur === "rarement" ? t("comparatif.rarement") : t("comparatif.non")}
      </span>
    </span>
  )
}

export function ComparatifFascicule() {
  return (
    <section className="mt-12 border-t border-border pt-10" aria-labelledby="comparatif-titre">
      <h2 id="comparatif-titre" className="font-display text-xl font-semibold">
        {t("comparatif.titre", { site: SITE_NAME })}
      </h2>
      <p className="mt-1.5 max-w-2xl text-sm text-muted-foreground">{t("comparatif.intro", { site: SITE_NAME })}</p>

      <div className="mt-5 overflow-x-auto rounded-xl border border-border">
        <table className="w-full min-w-[420px] text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/40 text-left">
              <th scope="col" className="px-4 py-3 font-medium">
                <span className="sr-only">{t("comparatif.colonne_critere")}</span>
              </th>
              <th scope="col" className="w-32 px-3 py-3 font-display font-semibold text-primary sm:w-40">
                {SITE_NAME}
              </th>
              <th scope="col" className="w-32 px-3 py-3 font-medium text-muted-foreground sm:w-40">
                {t("comparatif.fascicule")}
              </th>
            </tr>
          </thead>
          <tbody>
            {LIGNES.map((ligne) => (
              <tr key={ligne.cle} className="border-b border-border last:border-b-0">
                <th scope="row" className="px-4 py-3 text-left font-normal">
                  {t(`comparatif.${ligne.cle}`)}
                  <span className="block text-xs text-muted-foreground">
                    {t(`comparatif.${ligne.cle}_detail`)}
                  </span>
                </th>
                <td className="px-3 py-3">
                  <Cellule valeur="oui" />
                </td>
                <td className="px-3 py-3">
                  <Cellule valeur={ligne.fascicule} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="mt-3 max-w-2xl text-xs text-muted-foreground">{t("comparatif.note")}</p>
    </section>
  )
}
