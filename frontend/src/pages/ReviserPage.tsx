import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { BookOpen, FileText, Flame, Layers, ListChecks, NotebookPen, RotateCcw, Search, Sparkles, Timer, type LucideIcon } from "lucide-react"

import { getCartesDues, getErreurs } from "@/api/endpoints"
import { CLE_DUES } from "@/components/CartesDeRevision"
import { useNotesDues } from "@/components/RangeeNotes"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { coursListPath, epreuvesListPath, recherchePath, themesFrequentsPath } from "@/lib/countryPath"
import { cleErreurs } from "@/lib/erreurs"
import { ETAT_FOCUS_RECHERCHE } from "@/lib/recherche"
import { useSeo } from "@/lib/seo"
import { useNouvellesInedites } from "@/lib/useNouvellesInedites"
import { t, tn, useI18n } from "@/lib/i18n"

interface Carte {
  titre: string
  texte: string
  vers: string
  icone: LucideIcon
  /** Ce qui attend sur cette carte (« 12 erreurs à refaire »). Absent quand il n'y a rien : la carte, elle, reste. */
  signal?: string
}

/**
 * La page d'entrée de « Réviser », pour l'élève qui suit un plan : tout ce qui sert à réviser, rangé par ce qu'on veut
 * faire. « Réviser » ouvrait la liste des épreuves, et le reste tenait dans une rangée d'onglets dont un téléphone ne
 * montrait que la moitié ; « Mes erreurs » et « Mes cartes » n'y étaient pas du tout.
 *
 * Une carte sans rien à faire ne disparaît pas : son texte dit ce qu'on y trouvera, c'est ce qui fait découvrir la
 * fonction. Des liens vers les pages existantes, qui gardent leur adresse ; le visiteur garde son menu (voir Header).
 */
export function ReviserPage() {
  useI18n()
  useSeo({ title: t("nav.reviser") })
  const { country } = useCountry()
  const { isAuthenticated, user } = useAuth()
  const cursusId = user?.cursus_prepare?.id ?? null

  // Les mêmes clés de cache que l'accueil et Ma progression : un compteur ne dit jamais deux choses différentes.
  // Une requête en échec n'affiche rien : la carte mène à sa page, qui dira la panne.
  const erreurs =
    useQuery({
      queryKey: cleErreurs(cursusId),
      queryFn: ({ signal }) => getErreurs(cursusId as number, signal),
      enabled: isAuthenticated && cursusId !== null,
      retry: false,
    }).data?.total ?? 0
  const cartes =
    useQuery({
      queryKey: CLE_DUES,
      queryFn: ({ signal }) => getCartesDues(signal),
      enabled: isAuthenticated,
      retry: false,
    }).data?.total ?? 0
  const notes = useNotesDues(isAuthenticated)?.total ?? 0
  // La carte « Épreuves » mène alors droit aux inédites : c'est les regarder qui éteint le point or du menu.
  const { nouvelles } = useNouvellesInedites(country)

  const groupes: { cle: string; titre: string; cartes: Carte[] }[] = [
    {
      cle: "entrainer",
      titre: t("rv.entrainer"),
      cartes: [
        {
          titre: t("nav.epreuves"),
          texte: t("rv.epreuves"),
          icone: FileText,
          vers: nouvelles ? `${epreuvesListPath(country)}?origine=INEDITE` : epreuvesListPath(country),
          signal: nouvelles ? t("nav.nouvelles_inedites") : undefined,
        },
        { titre: t("qd.onglet_quiz"), texte: t("rv.quiz"), icone: ListChecks, vers: "/quiz" },
        { titre: t("blancs.onglet"), texte: t("rv.blancs"), icone: Timer, vers: "/examens-blancs" },
      ],
    },
    {
      cle: "apprendre",
      titre: t("rv.apprendre"),
      cartes: [
        { titre: t("nav.cours"), texte: t("rv.cours"), icone: BookOpen, vers: coursListPath(country) },
        { titre: t("fe.onglet"), texte: t("rv.fiches"), icone: Sparkles, vers: "/fiches-edukora" },
        { titre: t("qd.onglet_themes"), texte: t("rv.themes"), icone: Flame, vers: themesFrequentsPath(country) },
      ],
    },
    {
      cle: "revoir",
      titre: t("rv.revoir"),
      cartes: [
        {
          titre: t("erreurs.titre"),
          texte: t("rv.erreurs"),
          icone: RotateCcw,
          vers: "/erreurs",
          signal: erreurs > 0 ? tn("erreurs.total", erreurs) : undefined,
        },
        {
          titre: t("cartes.mes"),
          texte: t("rv.cartes"),
          icone: Layers,
          vers: "/cartes",
          signal: cartes > 0 ? tn("cartes.dues", cartes) : undefined,
        },
        {
          titre: t("cpt.carnet"),
          texte: t("rv.notes"),
          icone: NotebookPen,
          vers: notes > 0 ? "/carnet?reviser=1" : "/carnet",
          signal: notes > 0 ? tn("ca.notes_dues", notes) : undefined,
        },
      ],
    },
  ]

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">{t("nav.reviser")}</h1>
        <Link
          to={recherchePath(country)}
          state={ETAT_FOCUS_RECHERCHE}
          className="flex h-11 w-full items-center gap-2 rounded-full border border-border bg-card px-4 text-sm text-muted-foreground transition-colors hover:border-primary/50 hover:text-foreground sm:w-72"
        >
          <Search className="size-4 shrink-0" aria-hidden="true" />
          {t("qd.rechercher_site")}
        </Link>
      </div>

      {groupes.map((groupe) => (
        <section key={groupe.cle} aria-labelledby={`reviser-${groupe.cle}`} className="mt-7">
          <h2 id={`reviser-${groupe.cle}`} className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            {groupe.titre}
          </h2>
          {/* Deux colonnes sur un téléphone ; la troisième carte prend alors toute la largeur plutôt que de laisser un trou. */}
          <ul className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
            {groupe.cartes.map((carte) => (
              <li key={carte.titre} className="last:col-span-2 sm:last:col-span-1">
                <Link
                  to={carte.vers}
                  className="flex h-full flex-col rounded-2xl border border-border bg-card p-4 transition-colors hover:border-primary/40"
                >
                  <span className="flex items-center gap-2">
                    <carte.icone className="size-4 shrink-0 text-primary" aria-hidden="true" />
                    <span className="font-display text-base font-semibold leading-snug">{carte.titre}</span>
                  </span>
                  <span className="mt-1.5 text-xs text-muted-foreground">{carte.texte}</span>
                  {carte.signal && (
                    <span className="mt-2 w-fit rounded-lg bg-gold/15 px-2 py-1 text-xs font-semibold text-gold-text">
                      {carte.signal}
                    </span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  )
}
