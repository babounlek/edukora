import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { ArrowLeft, ThumbsDown, ThumbsUp } from "lucide-react"

import { ContactAide } from "@/components/aide/ContactAide"
import { ArticleMarkdown } from "@/components/aide/ArticleMarkdown"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useArticleAide } from "@/lib/aide/hooks"
import { remplirGabarits } from "@/lib/aide/texte"
import { trackEvent } from "@/lib/analytics"
import { ApiError } from "@/api/client"
import { langueCourante, localeCourante, t, useI18n } from "@/lib/i18n"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"

/** /aide/:slug : un article. Titre, réponse, « Cet article t'a aidé ? », puis la suite de la rubrique et le contact. */
export function AideArticlePage() {
  useI18n()
  const { slug } = useParams<{ slug: string }>()
  const { data: article, isPending, isError, error } = useArticleAide(slug)
  const [avis, setAvis] = useState<"oui" | "non" | null>(null)

  const titre = article ? remplirGabarits(article.titre) : t("aide.titre")
  // Un article non traduit s'affiche en français sous /en/help/… : il reste lisible mais n'est pas proposé aux moteurs
  // de recherche (le sitemap ne l'annonce pas non plus).
  useSeo({
    title: titre,
    description: article ? remplirGabarits(article.resume) : t("aide.seo_description", { site: SITE_NAME }),
    noindex: !!article && langueCourante() === "en" && !article.traduit,
  })

  useEffect(() => {
    setAvis(null)
  }, [slug])

  useEffect(() => {
    if (article) trackEvent("aide_article_vu", { slug: article.slug, categorie: article.categorie })
  }, [article])

  function repondre(valeur: "oui" | "non") {
    if (!article || avis) return
    setAvis(valeur)
    trackEvent("aide_article_utile", { slug: article.slug, utile: valeur === "oui" })
  }

  const introuvable = isError && error instanceof ApiError && error.status === 404

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-6 sm:py-10">
      <Link to="/aide" className="inline-flex min-h-10 items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground">
        <ArrowLeft className="size-4" aria-hidden="true" />
        {t("aide.article.retour")}
      </Link>

      {isPending && (
        <div className="mt-6 space-y-3" aria-busy="true">
          <Skeleton className="h-9 w-3/4" />
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
      )}

      {isError && (
        <div role="alert" className="mt-6 rounded-2xl border border-border bg-card p-6 text-center">
          <p className="font-medium">{introuvable ? t("aide.article.introuvable") : t("aide.erreur")}</p>
          <Button asChild variant="outline" className="mt-4 min-h-11">
            <Link to="/aide">{t("aide.article.retour")}</Link>
          </Button>
        </div>
      )}

      {article && (
        <article className="mt-4">
          <p className="text-sm font-medium text-primary">{t(`aide.cat.${article.categorie}` as Parameters<typeof t>[0], { site: SITE_NAME })}</p>
          <h1 className="mt-1 font-display text-2xl font-semibold leading-tight tracking-tight sm:text-3xl">{titre}</h1>
          <p className="mt-2 text-muted-foreground">{remplirGabarits(article.resume)}</p>
          {langueCourante() === "en" && !article.traduit && (
            <p className="mt-3 rounded-lg bg-muted px-3 py-2 text-sm text-muted-foreground">{t("aide.article.fr_seulement")}</p>
          )}

          <div className="mt-6 border-t border-border pt-2">
            <ArticleMarkdown corps={article.corps} />
          </div>

          <p className="mt-8 text-xs text-muted-foreground">
            {t("aide.article.maj", {
              date: new Date(article.maj_le).toLocaleDateString(localeCourante(), { day: "numeric", month: "long", year: "numeric" }),
            })}
          </p>

          <section aria-labelledby="aide-utile" className="mt-6 rounded-2xl border border-border bg-card p-5">
            {avis === null ? (
              <>
                <h2 id="aide-utile" className="font-medium">
                  {t("aide.article.utile_q")}
                </h2>
                <div className="mt-3 flex gap-2">
                  <Button type="button" variant="outline" className="min-h-11 flex-1 sm:flex-none" onClick={() => repondre("oui")}>
                    <ThumbsUp className="size-4" aria-hidden="true" />
                    {t("aide.article.oui")}
                  </Button>
                  <Button type="button" variant="outline" className="min-h-11 flex-1 sm:flex-none" onClick={() => repondre("non")}>
                    <ThumbsDown className="size-4" aria-hidden="true" />
                    {t("aide.article.non")}
                  </Button>
                </div>
              </>
            ) : (
              <p id="aide-utile" role="status" className="font-medium">
                {avis === "oui" ? t("aide.article.merci") : t("aide.article.merci_non")}
              </p>
            )}
          </section>

          {article.voisins.length > 0 && (
            <section className="mt-8" aria-labelledby="aide-voisins">
              <h2 id="aide-voisins" className="font-display text-lg font-semibold">
                {t("aide.article.meme_rubrique")}
              </h2>
              <ul className="mt-3 space-y-2">
                {article.voisins.map((voisin) => (
                  <li key={voisin.slug}>
                    <Link
                      to={`/aide/${voisin.slug}`}
                      className="flex min-h-12 items-center rounded-xl border border-border bg-card px-4 py-2.5 text-sm font-medium transition-colors hover:border-primary/40 hover:bg-accent/40"
                    >
                      {remplirGabarits(voisin.titre)}
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          )}

          <ContactAide source="article" article={{ slug: article.slug, titre }} className="mt-8" />
        </article>
      )}
    </div>
  )
}
