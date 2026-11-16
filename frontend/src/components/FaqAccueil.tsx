import { Link } from "react-router-dom"
import { ChevronDown } from "lucide-react"

import faq from "@/lib/faq-accueil.json"
import { trackEvent } from "@/lib/analytics"
import { langueCourante, t, useI18n } from "@/lib/i18n"
import { formatAmount } from "@/lib/utils"

/** Les questions de l'accueil dans la langue de l'interface, prix rempli. Même fichier que le HTML des moteurs. */
export function questionsAccueil(langue: "fr" | "en"): { q: string; r: string }[] {
  const prix = formatAmount(faq.prix_mois_fcfa)
  return faq[langue].map(({ q, r }) => ({ q, r: r.replace("{prix}", prix) }))
}

/**
 * Questions fréquentes de l'accueil (audit de l'accueil du 2026-11-15, R10) : ce qu'un élève ou un parent demande avant
 * d'essayer - ce qui est gratuit, le prix, le paiement, les examens couverts, le compte, le téléphone.
 *
 * Les textes vivent dans lib/faq-accueil.json, copié dans backend/catalog/faq_accueil.json (un test échoue si les deux
 * divergent) : le HTML servi aux moteurs de recherche porte les mêmes questions, avec le balisage FAQPage (voir
 * catalog.pages_statiques). Un moteur qui compare le HTML initial au rendu ne doit pas y voir deux pages différentes.
 *
 * `<details>` natif : ouvrable au clavier et sans JavaScript, et le texte des réponses reste dans la page.
 */
export function FaqAccueil() {
  useI18n()
  const questions = questionsAccueil(langueCourante())

  return (
    <section className="mx-auto max-w-5xl px-4 pb-10 sm:px-6" aria-labelledby="accueil-faq">
      <h2 id="accueil-faq" className="font-display text-xl font-semibold">
        {t("faq.titre")}
      </h2>
      <div className="mt-4 divide-y divide-border rounded-2xl border border-border bg-card">
        {questions.map(({ q, r }) => (
          <details key={q} className="group px-5">
            <summary className="flex min-h-12 cursor-pointer list-none items-center justify-between gap-3 py-3 font-medium [&::-webkit-details-marker]:hidden">
              {q}
              <ChevronDown className="size-4 shrink-0 text-muted-foreground transition-transform group-open:rotate-180" aria-hidden="true" />
            </summary>
            <p className="pb-4 text-sm text-muted-foreground">{r}</p>
          </details>
        ))}
      </div>
      <p className="mt-3 text-sm text-muted-foreground">
        {t("faq.autre_question")}{" "}
        <Link
          to="/aide"
          onClick={() => trackEvent("accueil_bouton_clic", { cible: "aide" })}
          className="font-medium text-primary underline-offset-4 hover:underline"
        >
          {t("faq.centre_aide")}
        </Link>
      </p>
    </section>
  )
}
