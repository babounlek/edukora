import { Link, useParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, SearchX } from "lucide-react"

import { getExamen } from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { ExamenPageData } from "@/api/types"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ErreurChargement } from "@/components/ErreurChargement"
import { FilAriane } from "@/components/FilAriane"
import { catalogueHomePath, epreuveDetailPath, epreuvesListPath, themesFrequentsPath } from "@/lib/countryPath"
import { useDeclarerLangueContenu } from "@/lib/langueContenu"
import { t, useI18n } from "@/lib/i18n"
import { useSeo } from "@/lib/seo"

/**
 * La page d'atterrissage d'un examen (`/cm/examens/bepc`) : ce que cherchent « annales BEPC Cameroun » ou « BAC D annales
 * corrigées ». Tout vient de l'API (chiffres, matières, épreuves récentes) : voir catalog.pages_examen côté serveur, qui
 * sert aussi le prérendu des moteurs avec le même contenu. Aucun corrigé n'y paraît, seulement des titres et des chiffres.
 */
export function ExamenPage() {
  useI18n()
  const { country, slug } = useParams<{ country: string; slug: string }>()

  const requete = useQuery({
    queryKey: ["examen", country, slug],
    queryFn: () => getExamen(country as string, slug as string),
    enabled: Boolean(country && slug),
    retry: (essais, erreur) => !(erreur instanceof ApiError && erreur.status === 404) && essais < 2,
  })
  const examen = requete.data

  useDeclarerLangueContenu(examen?.langue)
  useSeo({ title: examen?.textes.titre ?? t("ex.accueil"), description: examen?.textes.description })

  if (requete.isPending) return <ExamenSquelette />

  if (requete.isError) {
    const introuvable = requete.error instanceof ApiError && requete.error.status === 404
    return (
      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
        {introuvable ? (
          <div className="flex flex-col items-center gap-4 text-center">
            <SearchX className="size-10 text-muted-foreground" aria-hidden="true" />
            <p className="text-muted-foreground">{t("ex.introuvable")}</p>
            <Button asChild variant="outline">
              <Link to={epreuvesListPath(country as string)}>{t("ex.retour")}</Link>
            </Button>
          </div>
        ) : (
          <ErreurChargement message={t("ex.erreur")} onRetry={() => void requete.refetch()} />
        )}
      </div>
    )
  }

  return <ExamenContenu examen={examen as ExamenPageData} />
}

function ExamenSquelette() {
  return (
    // Un écran entier réservé : sinon le pied de page, juste sous ce petit squelette, saute à l'arrivée du contenu
    // (même cause et même remède que RouteFallback).
    <div className="mx-auto min-h-[100svh] max-w-3xl px-4 py-8 sm:px-6" aria-hidden="true">
      <Skeleton className="mb-3 h-8 w-2/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="mt-2 h-4 w-full" />
      <Skeleton className="mt-2 h-4 w-3/4" />
      <Skeleton className="mt-8 h-40 w-full" />
    </div>
  )
}

function Compteur({ valeur, libelle }: { valeur: number; libelle: string }) {
  return (
    <div className="rounded-xl border bg-card px-4 py-3">
      <p className="font-display text-2xl font-semibold leading-none">{valeur}</p>
      <p className="mt-1 text-xs text-muted-foreground">{libelle}</p>
    </div>
  )
}

function ExamenContenu({ examen }: { examen: ExamenPageData }) {
  const pays = examen.country
  // Les épreuves récentes, groupées par matière (l'ordre de la liste, plus récentes d'abord, est conservé).
  const parMatiere = new Map<string, ExamenPageData["epreuves"]>()
  for (const epreuve of examen.epreuves) {
    parMatiere.set(epreuve.matiere, [...(parMatiere.get(epreuve.matiere) ?? []), epreuve])
  }

  return (
    <article className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <FilAriane maillons={[{ libelle: t("ex.accueil"), to: catalogueHomePath(pays) }, { libelle: examen.libelle }]} />

      <h1 className="font-display text-3xl font-semibold leading-tight tracking-tight">{examen.textes.titre}</h1>
      <p className="mt-3 text-muted-foreground">{examen.textes.intro}</p>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Compteur valeur={examen.nb_epreuves} libelle={t("ex.c_epreuves")} />
        <Compteur valeur={examen.nb_epreuves_libres} libelle={t("ex.c_libres")} />
        <Compteur valeur={examen.nb_matieres} libelle={t("ex.c_matieres")} />
        {examen.annee_min && examen.annee_max ? (
          <div className="rounded-xl border bg-card px-4 py-3">
            <p className="font-display text-2xl font-semibold leading-none">{examen.annee_max}</p>
            <p className="mt-1 text-xs text-muted-foreground">
              {t("ex.c_annees", { debut: examen.annee_min, fin: examen.annee_max })}
            </p>
          </div>
        ) : null}
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        <Button asChild>
          <Link to={`${epreuvesListPath(pays)}?cursus=${examen.cursus_id}`}>
            {t("ex.voir_toutes", { libelle: examen.libelle })}
            <ArrowRight className="size-4" aria-hidden="true" />
          </Link>
        </Button>
        <Button asChild variant="outline">
          <Link to={`${themesFrequentsPath(pays)}?cursus=${examen.cursus_id}`}>{t("ex.themes")}</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/quiz">{t("ex.quiz")}</Link>
        </Button>
        <Button asChild variant="ghost">
          <Link to="/tarifs">{t("ex.prix")}</Link>
        </Button>
      </div>

      <section className="mt-10" aria-labelledby="ex-matieres">
        <h2 id="ex-matieres" className="text-xl font-semibold">
          {t("ex.matieres")}
        </h2>
        <ul className="mt-3 flex flex-wrap gap-2">
          {examen.matieres.map((m) => (
            <li key={m.label} className="rounded-full border bg-card px-3 py-1 text-sm">
              {m.label} <span className="text-muted-foreground">· {m.n}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-10" aria-labelledby="ex-recentes">
        <h2 id="ex-recentes" className="text-xl font-semibold">
          {t("ex.recentes")}
        </h2>
        {[...parMatiere.entries()].map(([matiere, epreuves]) => (
          <div key={matiere} className="mt-5">
            <h3 className="text-base font-semibold text-muted-foreground">{matiere}</h3>
            <ul className="mt-2 divide-y rounded-xl border bg-card">
              {epreuves.map((e) => (
                <li key={e.slug}>
                  <Link
                    to={epreuveDetailPath(pays, e.slug)}
                    className="flex min-h-12 items-center justify-between gap-3 px-4 py-2.5 hover:bg-muted/50"
                  >
                    <span className="text-sm font-medium">{e.title}</span>
                    <span
                      className={
                        e.libre
                          ? "shrink-0 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium text-primary"
                          : "shrink-0 text-xs text-muted-foreground"
                      }
                    >
                      {e.libre ? t("ex.corrige_libre") : t("ex.sujet_libre")}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>
    </article>
  )
}
