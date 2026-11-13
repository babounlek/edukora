import { Link, Navigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, CheckCircle2, Loader2, RotateCcw } from "lucide-react"

import { getErreurs } from "@/api/endpoints"
import type { ErreursMatiere } from "@/api/types"
import { ErreurChargement } from "@/components/ErreurChargement"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { EchecRefaireErreurs } from "@/components/MesErreurs"
import { cleErreurs, useRefaireErreurs } from "@/lib/erreurs"
import { couleurMatiere } from "@/lib/matiereCouleur"
import { useSeo } from "@/lib/seo"
import { subjectIcon } from "@/lib/subjectIcon"
import { capitaliserTheme, cn } from "@/lib/utils"
import { t, tn, useI18n } from "@/lib/i18n"

/**
 * « Mes erreurs » : les questions de quiz ratées et pas encore réussies, toutes matières confondues,
 * et de quoi les refaire en un geste.
 *
 * Avant cette page, refaire ses questions ratées n'existait que sur l'écran de résultat, pour le quiz
 * qu'on venait de finir, et plus jamais une fois la page quittée (audit produit du 2026-11-13). Ici
 * l'erreur devient un objet de travail : un compte qui baisse à chaque bonne réponse, un bouton.
 *
 * Rien n'est listé question par question : montrer l'énoncé à côté de « raté » reviendrait à donner la
 * réponse à relire au lieu de la retrouver. La page dit OÙ sont les erreurs (matière, thème), le quiz
 * les fait refaire.
 */
export function MesErreursPage() {
  useI18n()
  useSeo({ title: t("erreurs.titre") })
  const { isAuthenticated, isLoading: authLoading, user } = useAuth()
  const cursusId = user?.cursus_prepare?.id ?? null

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: cleErreurs(cursusId),
    queryFn: ({ signal }) => getErreurs(cursusId as number, signal),
    enabled: isAuthenticated && cursusId !== null,
  })
  const { lancer, enCours, echec } = useRefaireErreurs(cursusId)

  if (!authLoading && !isAuthenticated) {
    return <Navigate to="/connexion" state={{ from: "/erreurs" }} replace />
  }

  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 py-10 sm:px-6">
      <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
        <RotateCcw className="size-3.5" />
        {t("erreurs.titre")}
      </p>
      <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight sm:text-4xl">{t("erreurs.h1")}</h1>
      <p className="mt-2 text-sm text-muted-foreground">{t("erreurs.texte")}</p>

      {authLoading || (cursusId !== null && isLoading) ? (
        <div className="mt-8 flex flex-col gap-3">
          <Skeleton className="h-36 w-full rounded-3xl" />
          <Skeleton className="h-24 w-full rounded-2xl" />
        </div>
      ) : cursusId === null ? (
        <div className="mt-8 rounded-3xl border border-dashed border-border bg-card/60 p-8 text-center">
          <p className="mx-auto max-w-sm text-sm text-muted-foreground">{t("erreurs.sans_examen")}</p>
          <Button asChild className="mt-5 rounded-full">
            <Link to="/compte">{t("pc.choisir_cursus")}</Link>
          </Button>
        </div>
      ) : isError || !data ? (
        // Une panne n'est pas « aucune erreur » : l'élève se croirait à jour.
        <ErreurChargement objet={t("erreurs.objet")} onRetry={() => refetch()} className="mt-8" />
      ) : data.total === 0 ? (
        <div className="mt-8 rounded-3xl border border-dashed border-border bg-card/60 p-8 text-center">
          <span className="mx-auto flex size-12 items-center justify-center rounded-2xl bg-success/10 text-success">
            <CheckCircle2 className="size-6" />
          </span>
          <p className="mt-4 font-display text-lg font-semibold">{t("erreurs.vide")}</p>
          <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">{t("erreurs.vide_texte")}</p>
          <Button asChild className="mt-5 rounded-full">
            <Link to="/quiz">
              {t("erreurs.vide_bouton")}
              <ArrowRight />
            </Link>
          </Button>
        </div>
      ) : (
        <>
          <section className="mt-8 rounded-3xl border border-primary/20 bg-card p-5 shadow-lg shadow-primary/[0.06] sm:p-7">
            <p className="font-display text-3xl font-semibold leading-tight tracking-tight tabular-nums">
              {tn("erreurs.total", data.total)}
            </p>
            <Button
              size="lg"
              className="mt-5 h-12 w-full rounded-full text-base sm:w-auto sm:px-7"
              disabled={enCours !== null}
              onClick={() => lancer()}
            >
              {enCours === "tout" ? <Loader2 className="animate-spin" /> : <RotateCcw />}
              {enCours === "tout" ? t("quiz.preparation") : tn("erreurs.refaire", data.paquet)}
            </Button>
            <p className="mt-3 text-xs text-muted-foreground">{t("erreurs.refaire_note")}</p>
            <EchecRefaireErreurs echec={echec} />
          </section>

          <h2 className="mt-10 font-display text-xl font-semibold tracking-tight">{t("erreurs.par_matiere")}</h2>
          <ul className="mt-4 flex flex-col gap-3">
            {data.matieres.map((matiere) => (
              <LigneMatiere
                key={matiere.subject_id}
                matiere={matiere}
                enCours={enCours === matiere.subject_id}
                desactive={enCours !== null}
                onRefaire={() => lancer(matiere.subject_id)}
              />
            ))}
          </ul>
        </>
      )}
    </div>
  )
}

function LigneMatiere({
  matiere, enCours, desactive, onRefaire,
}: { matiere: ErreursMatiere; enCours: boolean; desactive: boolean; onRefaire: () => void }) {
  const Icone = subjectIcon(matiere.subject_code)
  const autres = matiere.themes_total - matiere.themes.length
  return (
    <li className="rounded-2xl border border-border bg-card p-4 sm:p-5">
      <div className="flex items-center gap-3">
        <span className={cn("flex size-10 shrink-0 items-center justify-center rounded-xl", couleurMatiere(matiere.subject_code).puce)}>
          <Icone className="size-5" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate font-display text-base font-semibold">{matiere.subject_label}</p>
          <p className="text-sm text-muted-foreground">{tn("erreurs.nb", matiere.nb)}</p>
        </div>
        <Button
          variant="outline"
          className="min-h-11 shrink-0 rounded-full"
          disabled={desactive}
          onClick={onRefaire}
          aria-label={t("erreurs.refaire_matiere_aria", { matiere: matiere.subject_label })}
        >
          {enCours ? <Loader2 className="animate-spin" /> : <RotateCcw />}
          {enCours ? t("quiz.preparation") : t("erreurs.refaire_matiere")}
        </Button>
      </div>
      {/* Les thèmes où les erreurs se concentrent : de quoi reconnaître ses lacunes d'un coup d'œil. */}
      <ul className="mt-3 flex flex-wrap gap-2">
        {matiere.themes.map((theme) => (
          <li key={theme.theme_id} className="max-w-full truncate rounded-full bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
            {capitaliserTheme(theme.theme)}
            {theme.nb > 1 && <span className="tabular-nums"> · {theme.nb}</span>}
          </li>
        ))}
        {autres > 0 && <li className="px-1 py-1 text-xs text-muted-foreground">{tn("erreurs.autres_themes", autres)}</li>}
      </ul>
    </li>
  )
}
