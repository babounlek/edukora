import { useEffect, useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { ArrowRight, BookOpenCheck, LifeBuoy, Search, X } from "lucide-react"

import { ContactAide } from "@/components/aide/ContactAide"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { useArticlesAide } from "@/lib/aide/hooks"
import { normaliser, rechercherArticles } from "@/lib/aide/recherche"
import { remplirGabarits } from "@/lib/aide/texte"
import { CATEGORIES_AIDE, type ArticleAideResume } from "@/lib/aide/types"
import { trackEvent } from "@/lib/analytics"
import { ouvrirCentre } from "@/lib/guides/etat"
import { t, tn, useI18n } from "@/lib/i18n"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"

function LigneArticle({ article }: { article: ArticleAideResume }) {
  return (
    <li>
      <Link
        to={`/aide/${article.slug}`}
        className="group flex min-h-14 items-center justify-between gap-3 rounded-xl border border-border bg-card px-4 py-3 transition-colors hover:border-primary/40 hover:bg-accent/40"
      >
        <span className="min-w-0">
          <span className="block font-medium leading-snug">{remplirGabarits(article.titre)}</span>
          <span className="mt-0.5 block text-sm text-muted-foreground">{remplirGabarits(article.resume)}</span>
        </span>
        <ArrowRight className="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
      </Link>
    </li>
  )
}

/** /aide : le centre d'aide. Recherche en haut, questions fréquentes, puis les rubriques. */
export function AidePage() {
  useI18n()
  useSeo({ title: t("aide.titre"), description: t("aide.seo_description", { site: SITE_NAME }) })
  const { data: articles, isPending, isError, refetch } = useArticlesAide()
  const [requete, setRequete] = useState("")

  const recherche = normaliser(requete).length > 0
  const resultats = useMemo(() => (articles && recherche ? rechercherArticles(articles, requete) : []), [articles, recherche, requete])

  // Une recherche sans réponse est le meilleur signal de ce qui manque dans l'aide : on le note (jamais le texte tapé),
  // une seule fois par pause de frappe et seulement pour une requête assez longue pour être une vraie question.
  useEffect(() => {
    if (!articles || !recherche || resultats.length > 0 || normaliser(requete).length < 3) return
    const minuteur = window.setTimeout(() => trackEvent("search_no_results", { source: "aide" }), 1200)
    return () => window.clearTimeout(minuteur)
  }, [articles, recherche, resultats.length, requete])

  const frequentes = (articles ?? []).filter((a) => a.populaire)

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-8 sm:py-12">
      <header className="text-center">
        <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
          <LifeBuoy className="size-6" aria-hidden="true" />
        </span>
        <h1 className="mt-4 font-display text-3xl font-semibold tracking-tight sm:text-4xl">{t("aide.titre")}</h1>
        <p className="mx-auto mt-2 max-w-xl text-muted-foreground">{t("aide.sous_titre", { site: SITE_NAME })}</p>
      </header>

      <div className="relative mt-6">
        <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" />
        <Input
          type="search"
          value={requete}
          onChange={(e) => setRequete(e.target.value)}
          aria-label={t("aide.recherche_label")}
          placeholder={t("aide.recherche_placeholder")}
          autoComplete="off"
          enterKeyHint="search"
          className="h-12 pl-10 pr-10 text-base"
        />
        {requete && (
          <button
            type="button"
            onClick={() => setRequete("")}
            aria-label={t("aide.recherche_effacer")}
            className="absolute right-1.5 top-1/2 flex size-9 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground hover:text-foreground"
          >
            <X className="size-4" aria-hidden="true" />
          </button>
        )}
      </div>

      {isPending && (
        <div className="mt-8 space-y-3" aria-busy="true">
          {[0, 1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-16 w-full rounded-xl" />
          ))}
        </div>
      )}

      {isError && (
        <div role="alert" className="mt-8 rounded-2xl border border-border bg-card p-5 text-center">
          <p className="text-sm text-muted-foreground">{t("aide.erreur")}</p>
          <Button type="button" variant="outline" className="mt-3 min-h-11" onClick={() => refetch()}>
            {t("aide.reessayer")}
          </Button>
        </div>
      )}

      {articles && recherche && (
        <section className="mt-8" aria-live="polite">
          {resultats.length > 0 ? (
            <>
              <p className="text-sm text-muted-foreground">{tn("aide.resultats", resultats.length)}</p>
              <ul className="mt-3 space-y-2.5">
                {resultats.map((article) => (
                  <LigneArticle key={article.slug} article={article} />
                ))}
              </ul>
            </>
          ) : (
            <div className="rounded-2xl border border-dashed border-border p-6 text-center">
              <p className="font-medium">{t("aide.aucun_resultat", { q: requete.trim() })}</p>
              <p className="mt-1 text-sm text-muted-foreground">{t("aide.aucun_resultat_aide")}</p>
            </div>
          )}
        </section>
      )}

      {articles && !recherche && (
        <>
          {frequentes.length > 0 && (
            <section className="mt-8" aria-labelledby="aide-frequentes">
              <h2 id="aide-frequentes" className="font-display text-xl font-semibold">
                {t("aide.frequentes")}
              </h2>
              <ul className="mt-3 space-y-2.5">
                {frequentes.map((article) => (
                  <LigneArticle key={article.slug} article={article} />
                ))}
              </ul>
            </section>
          )}

          <section className="mt-10" aria-labelledby="aide-rubriques">
            <h2 id="aide-rubriques" className="font-display text-xl font-semibold">
              {t("aide.parcourir")}
            </h2>
            <div className="mt-3 space-y-8">
              {CATEGORIES_AIDE.map((categorie) => {
                const liste = articles.filter((a) => a.categorie === categorie)
                if (liste.length === 0) return null
                return (
                  <div key={categorie}>
                    <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                      {t(`aide.cat.${categorie}` as Parameters<typeof t>[0], { site: SITE_NAME })}
                    </h3>
                    <ul className="mt-2 space-y-2.5">
                      {liste.map((article) => (
                        <LigneArticle key={article.slug} article={article} />
                      ))}
                    </ul>
                  </div>
                )
              })}
            </div>
          </section>
        </>
      )}

      <section className="mt-10 flex flex-col items-start gap-3 rounded-2xl bg-muted/50 p-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <BookOpenCheck className="mt-0.5 size-5 shrink-0 text-primary" aria-hidden="true" />
          <div>
            <h2 className="font-medium">{t("aide.guides_titre")}</h2>
            <p className="text-sm text-muted-foreground">{t("aide.guides_texte")}</p>
          </div>
        </div>
        <Button type="button" variant="outline" className="min-h-11 w-full sm:w-auto" onClick={ouvrirCentre}>
          {t("aide.guides_bouton")}
        </Button>
      </section>

      <ContactAide source="centre" className="mt-6" />
    </div>
  )
}
