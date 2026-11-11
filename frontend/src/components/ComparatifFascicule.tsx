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

// Clés complètes (et non `comparatif.${cle}`) : `t` n'accepte que des clés connues
// du dictionnaire, un gabarit de chaîne ferait échouer `tsc -b`.
interface Ligne {
  libelle: Parameters<typeof t>[0]
  detail: Parameters<typeof t>[0]
  fascicule: Valeur
}

const LIGNES: Ligne[] = [
  { libelle: "comparatif.corriges", detail: "comparatif.corriges_detail", fascicule: "oui" },
  { libelle: "comparatif.cours", detail: "comparatif.cours_detail", fascicule: "rarement" },
  { libelle: "comparatif.quiz", detail: "comparatif.quiz_detail", fascicule: "non" },
  { libelle: "comparatif.themes", detail: "comparatif.themes_detail", fascicule: "rarement" },
  { libelle: "comparatif.suivi", detail: "comparatif.suivi_detail", fascicule: "non" },
  { libelle: "comparatif.maj", detail: "comparatif.maj_detail", fascicule: "non" },
]

const LIBELLE_VALEUR: Record<Valeur, Parameters<typeof t>[0]> = {
  oui: "comparatif.oui",
  non: "comparatif.non",
  rarement: "comparatif.rarement",
}

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

      {/* Mobile : une carte par fonction plutôt qu'un tableau de 420 px mini, dont la 3e colonne
          sortait de l'écran (« Un fa… », « Ra… ») sans rien signaler. */}
      <ul role="list" className="mt-5 divide-y divide-border rounded-xl border border-border sm:hidden">
        {LIGNES.map((ligne) => (
          <li key={ligne.libelle} className="px-4 py-3">
            <p className="text-sm font-medium">{t(ligne.libelle)}</p>
            <p className="text-xs text-muted-foreground">{t(ligne.detail)}</p>
            <div className="mt-2 flex flex-wrap gap-2 text-xs">
              <span className="inline-flex items-center gap-1 rounded-full bg-success/10 px-2.5 py-1 font-medium text-success">
                <Check className="size-3.5" aria-hidden />
                {SITE_NAME}
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2.5 py-1 text-muted-foreground">
                {ligne.fascicule === "oui" ? (
                  <Check className="size-3.5" aria-hidden />
                ) : (
                  <Minus className="size-3.5" aria-hidden />
                )}
                {t("comparatif.fascicule_court")} : {t(LIBELLE_VALEUR[ligne.fascicule])}
              </span>
            </div>
          </li>
        ))}
      </ul>

      <div className="mt-5 hidden overflow-x-auto rounded-xl border border-border sm:block">
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
              <tr key={ligne.libelle} className="border-b border-border last:border-b-0">
                <th scope="row" className="px-4 py-3 text-left font-normal">
                  {t(ligne.libelle)}
                  <span className="block text-xs text-muted-foreground">
                    {t(ligne.detail)}
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
