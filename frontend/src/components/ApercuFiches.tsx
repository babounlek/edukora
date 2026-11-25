import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, BadgeCheck, Brain, ListChecks, NotebookPen, TextSelect } from "lucide-react"

import { getFichesApercu } from "@/api/endpoints"
import type { FicheApercu } from "@/api/types"
import { NoteTexte } from "@/components/NoteTexte"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"
import { useCursusDeclare } from "@/lib/cursusAccueil"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

/** Les fiches gratuites à montrer : celles de l'examen déclaré, à défaut celles du pays. Vide tant qu'aucune n'est publiée. */
export function useApercuFiches(country: string) {
  const cursus = useCursusDeclare()
  return useQuery({
    queryKey: ["fiches-edukora", "apercu", country, cursus],
    queryFn: ({ signal }) => getFichesApercu(country, cursus, signal),
    enabled: Boolean(country),
    staleTime: 5 * 60 * 1000,
  }).data
}

function lienFiche(f: FicheApercu): string {
  return `/fiches-edukora?cursus=${f.cursus_id}&matiere=${f.matiere_id}&fiche=${f.id}`
}

/** Une fiche en aperçu : la notion, les années où elle est tombée, et le début de sa définition, lisible sans compte. */
function CarteApercu({ fiche }: { fiche: FicheApercu }) {
  const annees = fiche.sessions.filter((s) => s.origine === "OFFICIEL").map((s) => s.annee)
  return (
    <Link
      to={lienFiche(fiche)}
      className="group relative flex h-full flex-col overflow-hidden rounded-2xl border border-border bg-card p-4 pl-5 transition-all duration-300 hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/10"
    >
      <span aria-hidden="true" className={cn("absolute inset-y-0 left-0 w-1", couleurMatiere(fiche.matiere_code).barre)} />
      <span className="text-xs font-medium text-muted-foreground">
        {fiche.matiere} · {fiche.examen}
      </span>
      <span className="mt-1 font-display text-lg font-semibold leading-tight tracking-tight">{fiche.terme}</span>
      {annees.length > 0 && (
        <span className="mt-2 flex flex-wrap items-center gap-1 text-xs">
          <span className="font-medium text-gold-text">{tn("fe.tombe", annees.length)}</span>
          {annees.map((a) => (
            <span key={a} className="rounded-full bg-gold/15 px-1.5 py-0.5 font-semibold tabular-nums text-gold-text">
              {a}
            </span>
          ))}
        </span>
      )}
      <span className="mt-2.5 block max-h-[6.2rem] overflow-hidden [mask-image:linear-gradient(to_bottom,black_60%,transparent)]">
        <NoteTexte texte={fiche.definition ?? ""} />
      </span>
    </Link>
  )
}

/** Les fiches gratuites en aperçu, avec le lien vers toutes les fiches. Rien tant qu'aucune fiche n'est publiée. */
export function ApercuFiches({ country, className }: { country: string; className?: string }) {
  useI18n()
  const data = useApercuFiches(country)
  if (!data || data.fiches.length === 0) return null
  return (
    <section className={className} aria-labelledby="apercu-fiches-titre">
      <div className="flex flex-wrap items-end justify-between gap-x-4 gap-y-2">
        <div className="min-w-0">
          <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-gold-text">
            <BadgeCheck className="size-3.5" aria-hidden="true" />
            {t("fe.apercu_surtitre")}
          </p>
          <h2 id="apercu-fiches-titre" className="mt-1.5 font-display text-2xl font-semibold tracking-tight">
            {t("fe.titre")}
          </h2>
          <p className="mt-1 max-w-xl text-sm text-muted-foreground">{t("fe.apercu_texte")}</p>
        </div>
        <Link to={lienFiche(data.fiches[0]).replace(/&fiche=\d+$/, "")} className="inline-flex shrink-0 items-center gap-1 text-sm font-medium text-primary hover:underline">
          {tn("fe.voir_toutes", data.total)}
          <ArrowRight className="size-3.5" aria-hidden="true" />
        </Link>
      </div>
      <ul className="mt-4 grid items-stretch gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data.fiches.map((f) => (
          <li key={f.id}>
            <CarteApercu fiche={f} />
          </li>
        ))}
      </ul>
    </section>
  )
}

/**
 * L'accueil du visiteur et de l'élève sans abonnement : les notes (ce que l'on garde et revoit) puis les Fiches EduKora en
 * aperçu gratuit. Les notes sont gratuites avec un compte ; les fiches ne sont annoncées que s'il y en a de publiées.
 */
export function SectionNotesAccueil({ country }: { country: string }) {
  useI18n()
  const { isAuthenticated } = useAuth()
  const gestes = [
    { Icone: TextSelect, titre: t("an.geste1_titre"), texte: t("an.geste1_texte") },
    { Icone: ListChecks, titre: t("an.geste2_titre"), texte: t("an.geste2_texte") },
    { Icone: Brain, titre: t("an.geste3_titre"), texte: t("an.geste3_texte") },
  ]
  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 sm:py-14">
      <section aria-labelledby="accueil-notes-visiteur-titre">
        <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
          <NotebookPen className="size-3.5" aria-hidden="true" />
          {t("cpt.carnet")}
        </p>
        <h2 id="accueil-notes-visiteur-titre" className="mt-1.5 font-display text-2xl font-semibold tracking-tight">
          {t("an.titre")}
        </h2>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{t("an.texte")}</p>
        <ul className="mt-5 grid gap-4 sm:grid-cols-3">
          {gestes.map((g) => (
            <li key={g.titre} className="rounded-2xl border border-border bg-card p-4">
              <span className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <g.Icone className="size-5" aria-hidden="true" />
              </span>
              <p className="mt-3 font-display text-base font-semibold">{g.titre}</p>
              <p className="mt-1 text-sm text-muted-foreground">{g.texte}</p>
            </li>
          ))}
        </ul>
        <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-2">
          <Button asChild className="rounded-full">
            {isAuthenticated ? (
              <Link to="/carnet">
                {t("an.ouvrir")}
                <ArrowRight />
              </Link>
            ) : (
              <Link to="/connexion" state={{ from: "/carnet" }}>
                {t("an.creer_compte")}
                <ArrowRight />
              </Link>
            )}
          </Button>
          <span className="text-xs text-muted-foreground">{t("an.gratuit")}</span>
        </div>
      </section>
      <ApercuFiches country={country} className="mt-12" />
    </div>
  )
}
