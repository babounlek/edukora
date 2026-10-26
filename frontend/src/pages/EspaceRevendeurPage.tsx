import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { useInfiniteQuery, useQuery } from "@tanstack/react-query"
import { Check, Copy, Loader2, MessageCircle, RefreshCw } from "lucide-react"
import { toast } from "sonner"

import { ApiError } from "@/api/client"
import { getEspaceRevendeur, listVentesRevendeur } from "@/api/endpoints"
import type { EspaceRevendeur, EtatCommission, StatutRevendeur, VenteRevendeur } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { localeCourante, t, tn, useI18n } from "@/lib/i18n"
import { lienDeRevendeur } from "@/lib/referral"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import { cn, formatAmount } from "@/lib/utils"

/** Un état = un libellé ET une couleur, jamais la couleur seule. « Retenue » reste neutre : c'est un contrôle, pas un refus. */
const ETATS: Record<EtatCommission, string> = {
  EN_ATTENTE: "text-warning-foreground dark:text-warning",
  ACQUISE: "text-success",
  RETENUE: "text-muted-foreground",
  PAYEE: "text-success",
  ANNULEE: "text-destructive",
}

/** Le message d'un compte qui n'est pas (ou plus) pleinement actif ; rien pour un compte actif. */
function bandeauDe(statut: StatutRevendeur): string | null {
  if (statut === "EN_ATTENTE") return t("rev.statut_en_attente")
  if (statut === "SUSPENDU") return t("rev.statut_suspendu")
  if (statut === "RESILIE") return t("rev.statut_resilie")
  return null
}

function dateCourte(iso: string): string {
  return new Date(iso).toLocaleDateString(localeCourante(), { day: "numeric", month: "short", year: "numeric" })
}

export function EspaceRevendeurPage() {
  useI18n()
  useSeo({ title: t("rev.titre"), noindex: true })

  const { isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) navigate("/connexion", { state: { from: "/espace-revendeur" } })
  }, [isLoading, isAuthenticated, navigate])

  const espace = useQuery({
    queryKey: ["revendeur", "moi"],
    queryFn: ({ signal }) => getEspaceRevendeur(signal),
    enabled: isAuthenticated,
    // Un compte qui n'est pas revendeur reçoit 404 : inutile de réessayer.
    retry: (nombre, err) => !(err instanceof ApiError && err.status < 500) && nombre < 2,
  })

  if (isLoading || !isAuthenticated) return null

  return (
    <div className="mx-auto max-w-4xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <header className="mb-8">
        <h1 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">{t("rev.titre")}</h1>
        <p className="mt-2 max-w-xl text-muted-foreground">{t("rev.sous_titre")}</p>
      </header>

      {espace.isPending ? (
        <div className="flex flex-col gap-3" aria-busy="true" aria-label={t("rev.chargement")}>
          <Skeleton className="h-32 rounded-2xl" />
          <Skeleton className="h-28 rounded-2xl" />
        </div>
      ) : espace.error instanceof ApiError && espace.error.status === 404 ? (
        <div className="rounded-2xl border border-dashed border-border px-6 py-12 text-center">
          <p className="font-display text-lg font-semibold">{t("rev.pas_revendeur")}</p>
          <p className="mx-auto mt-1.5 max-w-sm text-sm text-muted-foreground">{t("rev.pas_revendeur_texte")}</p>
          <Button asChild variant="outline" className="mt-5 rounded-full">
            <Link to="/compte">{t("compte.mon_compte")}</Link>
          </Button>
        </div>
      ) : espace.isError ? (
        <div role="alert" className="flex items-center justify-between gap-4 rounded-2xl border border-border bg-card px-5 py-4">
          <p className="text-sm text-muted-foreground">{t("rev.erreur")}</p>
          <Button onClick={() => void espace.refetch()} variant="outline" size="sm" className="shrink-0 rounded-full">
            <RefreshCw className="size-3.5" />
            {t("erreur.reessayer")}
          </Button>
        </div>
      ) : (
        <Tableau espace={espace.data} />
      )}
    </div>
  )
}

function Tableau({ espace }: { espace: EspaceRevendeur }) {
  const bandeau = bandeauDe(espace.statut)
  return (
    <div className="flex flex-col gap-6">
      <p className="text-sm font-medium text-foreground/80">
        {espace.nom_affiche} · {t(`rev.type_${espace.type}`)}
      </p>

      {bandeau && (
        <p role="status" className="rounded-xl border border-warning/40 bg-warning/10 px-4 py-3 text-sm">
          {bandeau}
        </p>
      )}

      <Partage code={espace.code} />

      <section aria-labelledby="rev-commissions">
        <h2 id="rev-commissions" className="mb-3 font-display text-xl font-semibold">{t("rev.commissions_titre")}</h2>
        <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Montant libelle={t("rev.m_en_attente")} aide={t("rev.m_en_attente_aide")} valeur={espace.montants.en_attente} />
          <Montant libelle={t("rev.m_acquise")} aide={t("rev.m_acquise_aide")} valeur={espace.montants.acquise} fort />
          <Montant libelle={t("rev.m_retenue")} aide={t("rev.m_retenue_aide")} valeur={espace.montants.retenue} />
          <Montant libelle={t("rev.m_payee")} aide={t("rev.m_payee_aide")} valeur={espace.montants.payee} />
        </dl>
        <div className="mt-4 space-y-1 text-sm text-muted-foreground">
          <p>{t("rev.taux", { taux: espace.taux_base_pct })}</p>
          {espace.palier && <p>{t("rev.palier", { seuil: espace.palier.seuil, taux: espace.palier.taux_pct })}</p>}
          <p>
            {tn("rev.ventes_mois", espace.ventes_du_mois)} · {tn("rev.clients", espace.nb_clients)}
          </p>
        </div>
      </section>

      <Ventes />
    </div>
  )
}

function Montant({ libelle, aide, valeur, fort = false }: { libelle: string; aide: string; valeur: number; fort?: boolean }) {
  return (
    <div className={cn("rounded-2xl border bg-card p-4", fort ? "border-primary/40 ring-1 ring-primary/20" : "border-border")}>
      <dt className="text-xs font-medium text-muted-foreground">{libelle}</dt>
      <dd className="mt-1 font-display text-2xl font-semibold tabular-nums leading-tight">
        {formatAmount(valeur)}
        <span className="ml-1 text-xs font-medium text-muted-foreground">FCFA</span>
      </dd>
      <p className="mt-1 text-xs text-muted-foreground">{aide}</p>
    </div>
  )
}

function Partage({ code }: { code: string }) {
  const [copie, setCopie] = useState(false)
  const lien = lienDeRevendeur(code)
  const message = t("rev.whatsapp_message", { site: SITE_NAME, lien })

  function copier() {
    // navigator.clipboard est absent hors contexte sécurisé : on n'affiche « copié » qu'une fois la copie faite.
    Promise.resolve()
      .then(() => navigator.clipboard.writeText(lien))
      .then(() => {
        setCopie(true)
        setTimeout(() => setCopie(false), 2000)
      })
      .catch(() => toast.error(t("rev.copie_erreur")))
  }

  return (
    <section aria-labelledby="rev-partage" className="rounded-2xl border border-border bg-card p-5">
      <h2 id="rev-partage" className="font-display text-lg font-semibold">{t("rev.partage_titre")}</h2>
      <p className="mt-3 w-fit rounded-lg bg-muted px-3 py-1.5 font-mono text-xl font-semibold tracking-widest">{code}</p>
      <p className="mt-3 break-all text-sm text-muted-foreground">{lien}</p>
      <p className="mt-2 max-w-xl text-xs text-muted-foreground">{t("rev.partage_aide")}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button onClick={copier} variant="outline" className="rounded-full">
          {copie ? <Check className="size-4 text-success" /> : <Copy className="size-4" />}
          {copie ? t("rev.copie") : t("rev.copier_lien")}
        </Button>
        <Button asChild className="rounded-full">
          <a href={`https://wa.me/?text=${encodeURIComponent(message)}`} target="_blank" rel="noopener noreferrer">
            <MessageCircle className="size-4" />
            {t("rev.whatsapp")}
          </a>
        </Button>
      </div>
    </section>
  )
}

function Ventes() {
  const ventes = useInfiniteQuery({
    queryKey: ["revendeur", "ventes"],
    queryFn: ({ pageParam, signal }) => listVentesRevendeur(pageParam, signal),
    initialPageParam: 1,
    getNextPageParam: (derniere, pages) => (derniere.next ? pages.length + 1 : undefined),
  })
  const lignes: VenteRevendeur[] = ventes.data?.pages.flatMap((page) => page.results) ?? []

  return (
    <section aria-labelledby="rev-ventes">
      <h2 id="rev-ventes" className="mb-3 font-display text-xl font-semibold">{t("rev.ventes_titre")}</h2>

      {ventes.isPending ? (
        <Skeleton className="h-24 rounded-2xl" />
      ) : ventes.isError ? (
        <div role="alert" className="flex items-center justify-between gap-4 rounded-2xl border border-border bg-card px-5 py-4">
          <p className="text-sm text-muted-foreground">{t("rev.erreur")}</p>
          <Button onClick={() => void ventes.refetch()} variant="outline" size="sm" className="shrink-0 rounded-full">
            <RefreshCw className="size-3.5" />
            {t("erreur.reessayer")}
          </Button>
        </div>
      ) : lignes.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-border px-6 py-10 text-center">
          <p className="font-display text-lg font-semibold">{t("rev.ventes_vide")}</p>
          <p className="mx-auto mt-1.5 max-w-sm text-sm text-muted-foreground">{t("rev.ventes_vide_texte")}</p>
        </div>
      ) : (
        <>
          <ul className="flex flex-col gap-2">
            {lignes.map((vente) => (
              <li key={vente.id} className="flex items-start justify-between gap-3 rounded-xl border border-border bg-card px-4 py-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold">{vente.client}</p>
                  <p className="truncate text-xs text-muted-foreground">
                    {vente.plan} · {dateCourte(vente.created_at)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {t("rev.ligne_base", { base: formatAmount(vente.base_fcfa), taux: vente.taux_pct })}
                  </p>
                </div>
                <div className="shrink-0 text-right">
                  <p className="font-display text-base font-semibold tabular-nums">
                    +{formatAmount(vente.montant_fcfa)}
                    <span className="ml-1 text-xs font-medium text-muted-foreground">FCFA</span>
                  </p>
                  <p className={cn("text-xs font-semibold", ETATS[vente.etat])}>{t(`rev.etat_${vente.etat}`)}</p>
                </div>
              </li>
            ))}
          </ul>
          {ventes.hasNextPage && (
            <div className="mt-4 text-center">
              <Button
                onClick={() => void ventes.fetchNextPage()}
                disabled={ventes.isFetchingNextPage}
                variant="outline"
                className="rounded-full"
              >
                {ventes.isFetchingNextPage && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
                {t("rev.voir_plus")}
              </Button>
            </div>
          )}
        </>
      )}
    </section>
  )
}
