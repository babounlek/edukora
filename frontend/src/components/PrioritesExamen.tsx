import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, Compass, Sparkles } from "lucide-react"

import { getPlanDuJour, getPriorites } from "@/api/endpoints"
import type { PrioriteMatiere } from "@/api/types"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { subjectIcon } from "@/lib/subjectIcon"
import { formatCompteARebours } from "@/components/CompteAReboursBadge"
import { Ecrin } from "@/components/Progression"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { capitaliserTheme, cn } from "@/lib/utils"

/**
 * "Tes priorités pour le BAC D" : la restitution du diagnostic d'accueil - où
 * concentrer son temps, et pourquoi.
 *
 * Trois choses dites honnêtement. Le classement vient surtout du coefficient (un fait
 * lu dans les épreuves réelles), nuancé par les réponses de l'élève ; on n'affiche
 * jamais de pourcentage sur trois réponses, seulement "2 sur 3" ; et le bloc dit
 * lui-même que c'est un repère, pas un niveau. Un diagnostic présenté comme un verdict
 * fait peur ou flatte à tort - dans les deux cas l'élève cesse de croire ce qu'on lui
 * propose ensuite.
 *
 * Se termine sur la SÉANCE que le plan lui propose vraiment (même donnée que l'accueil),
 * pour que "priorités" et "première séance" ne se contredisent jamais à l'écran.
 */
export function PrioritesExamen({ cursusId, className }: { cursusId: number; className?: string }) {
  const { country } = useCountry()
  const { user } = useAuth()

  const { data } = useQuery({
    queryKey: ["priorites", cursusId],
    queryFn: ({ signal }) => getPriorites(cursusId, signal),
    retry: false,
  })
  const { data: plan } = useQuery({
    queryKey: ["plan-du-jour"],
    queryFn: ({ signal }) => getPlanDuJour(signal),
    enabled: Boolean(user),
  })

  // Les barres partent de zéro puis se remplissent : c'est ce qui fait "lire" le
  // classement plutôt que le recevoir d'un bloc.
  const [pret, setPret] = useState(false)
  useEffect(() => {
    const t = setTimeout(() => setPret(true), 150)
    return () => clearTimeout(t)
  }, [])

  if (!data || data.matieres.length === 0) return null

  const examen = user?.cursus_prepare
    ? `${user.cursus_prepare.examen_display}${user.cursus_prepare.series ? ` ${user.cursus_prepare.series.code}` : ""}`
    : null
  const compte = data.compte_a_rebours ? formatCompteARebours(data.compte_a_rebours) : ""
  const tete = data.matieres.filter((m) => m.prioritaire)
  const titreSeance = plan?.seance && !plan.seance.verrouillee ? plan.seance.theme?.name ?? plan.seance.savoir?.intitule : null

  return (
    <div className={className}>
      <Ecrin>
        <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
          <Compass className="size-3.5" />
          Ton point de départ
        </p>
        <h2 className="mt-2 font-display text-3xl font-semibold leading-[1.1] tracking-tight text-balance sm:text-4xl">
          Tes priorités pour {examen ? `le ${examen}` : "ton examen"}
        </h2>
        <p className="mt-2 max-w-xl text-sm text-muted-foreground">
          {compte && <span className="font-medium text-foreground">{compte}</span>}
          {compte && " · "}
          {tete.length > 1
            ? `On commence par ces ${tete.length} matières : ce sont elles qui rapportent le plus à travailler maintenant.`
            : "Voici où concentrer ton temps."}
        </p>

        <ol className="mt-6 grid gap-3 sm:grid-cols-3">
          {tete.map((matiere, index) => (
            <li
              key={matiere.subject_id}
              className="animate-fade-up rounded-2xl border border-gold/30 bg-gold/[0.06] p-4"
              style={{ animationDelay: `${index * 90}ms` }}
            >
              <div className="flex items-center justify-between">
                <span className="flex size-8 items-center justify-center rounded-full bg-gradient-to-br from-gold to-gold/70 font-display text-base font-semibold text-gold-foreground shadow-sm shadow-gold/30">
                  {matiere.rang}
                </span>
                <IconeMatiere code={matiere.subject_code} />
              </div>
              <p className="mt-3 font-display text-lg font-semibold leading-tight">{matiere.subject_label}</p>
              <Repere matiere={matiere} className="mt-2" />
              {matiere.coefficient !== null && (
                <p className="mt-2 text-xs text-muted-foreground">Coefficient {formatCoef(matiere.coefficient)} à l'examen</p>
              )}
            </li>
          ))}
        </ol>

        {data.matieres.length > tete.length && (
          <div className="mt-7">
            <h3 className="text-sm font-semibold">Toutes tes matières</h3>
            <ul className="mt-3 flex flex-col gap-2.5">
              {data.matieres.map((matiere) => (
                <li key={matiere.subject_id} className="grid grid-cols-[minmax(0,9rem)_1fr] items-center gap-3 text-sm sm:grid-cols-[minmax(0,12rem)_1fr]">
                  <span className="truncate" title={matiere.subject_label}>
                    {matiere.subject_label}
                    {matiere.coefficient !== null && (
                      <span className="ml-1.5 text-xs text-muted-foreground">×{formatCoef(matiere.coefficient)}</span>
                    )}
                  </span>
                  <span
                    className="h-2.5 overflow-hidden rounded-full bg-muted"
                    role="img"
                    aria-label={`${matiere.subject_label} : priorité ${matiere.rang}`}
                  >
                    <span
                      className={cn(
                        "block h-full rounded-full transition-[width] duration-1000 ease-out",
                        matiere.prioritaire ? "bg-gradient-to-r from-gold/80 to-gold" : "bg-primary/45",
                      )}
                      style={{ width: pret ? `${Math.max(matiere.urgence, 4)}%` : "0%" }}
                    />
                  </span>
                </li>
              ))}
            </ul>
            <p className="mt-2 text-xs text-muted-foreground">
              Plus la barre est longue, plus cette matière mérite ton temps en ce moment.
            </p>
          </div>
        )}

        {data.themes_a_travailler.length > 0 && (
          <div className="mt-7">
            <h3 className="text-sm font-semibold">À reprendre en premier</h3>
            <p className="mt-0.5 text-xs text-muted-foreground">Les thèmes qui t'ont résisté pendant le diagnostic.</p>
            <ul className="mt-2 flex flex-wrap gap-2">
              {data.themes_a_travailler.map((theme) => (
                <li
                  key={`${theme.subject_label}-${theme.theme}`}
                  className="rounded-full border border-border bg-background/70 px-3 py-1 text-xs font-medium"
                >
                  {capitaliserTheme(theme.theme)}
                  <span className="text-muted-foreground"> · {theme.subject_label}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-8 flex flex-col gap-3 border-t border-border/60 pt-6 sm:flex-row sm:items-center">
          <Button
            asChild
            size="lg"
            className="group h-12 rounded-full px-7 text-base shadow-lg shadow-primary/25 transition-all hover:-translate-y-0.5 hover:shadow-xl hover:shadow-primary/30"
          >
            <Link to={`/${country}`}>
              <Sparkles className="size-4" />
              Commencer ma première séance
              <ArrowRight className="size-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </Button>
          {titreSeance && (
            <p className="min-w-0 text-sm text-muted-foreground">
              Au programme : <span className="font-medium text-foreground">{capitaliserTheme(titreSeance)}</span>
            </p>
          )}
        </div>
        <p className="mt-4 text-xs text-muted-foreground">
          Quelques questions par matière donnent un repère, pas un niveau. Ton plan s'ajuste à chaque séance.
        </p>
      </Ecrin>
    </div>
  )
}

function IconeMatiere({ code }: { code: string }) {
  const Icone = subjectIcon(code)
  return (
    <span className={cn("flex size-9 items-center justify-center rounded-xl", couleurMatiere(code).puce)}>
      <Icone className="size-[18px]" />
    </span>
  )
}

/** "2 sur 3" en pastilles : lisible sans chiffre, et sans prétendre à un pourcentage. */
function Repere({ matiere, className }: { matiere: PrioriteMatiere; className?: string }) {
  if (matiere.total === 0) {
    return <p className={cn("text-xs text-muted-foreground", className)}>Pas encore sondée</p>
  }
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <span
        className="flex gap-1"
        role="img"
        aria-label={`${matiere.reussies} réussie${matiere.reussies > 1 ? "s" : ""} sur ${matiere.total}`}
      >
        {Array.from({ length: matiere.total }).map((_, i) => (
          <span
            key={i}
            className={cn("size-2.5 rounded-full", i < matiere.reussies ? "bg-primary" : "bg-muted ring-1 ring-border")}
          />
        ))}
      </span>
      <span className="text-xs text-muted-foreground">
        {matiere.reussies} sur {matiere.total} · {LIBELLE_NIVEAU[matiere.niveau]}
      </span>
    </div>
  )
}

const LIBELLE_NIVEAU: Record<PrioriteMatiere["niveau"], string> = {
  a_situer: "à situer",
  fragile: "à consolider",
  moyen: "en bonne voie",
  solide: "solide",
}

/** "4" et non "4.0", "1,5" à la française. */
function formatCoef(valeur: number): string {
  return Number.isInteger(valeur) ? String(valeur) : String(valeur).replace(".", ",")
}

