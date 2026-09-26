import { useQuery } from "@tanstack/react-query"
import { ArrowRight, Sparkles, Trophy } from "lucide-react"

import { getBilanPeriode } from "@/api/endpoints"
import type { BilanPeriode } from "@/api/types"
import { Ecrin } from "@/components/Progression"
import { jalonsAtteints, prochainJalon } from "@/lib/jalons"

/**
 * "Ta semaine" : ce qui a été fait sur 7 jours, les paliers franchis, et le prochain.
 *
 * Le bilan mensuel (voir BilanDePeriode) sert à décider de renouveler ; celui-ci sert à
 * revenir demain. Même règles d'honnêteté : rien d'inventé, aucune baisse commentée, et le
 * bloc disparaît quand il n'y a encore rien à raconter - sauf un premier palier à viser,
 * qui est justement ce qui donne envie de commencer.
 *
 * Les jalons sont des paliers de travail (séances, questions, thèmes solides), jamais des
 * points : rien à perdre, rien qui se remette à zéro (voir lib/jalons).
 */
export function TaSemaine({ cursusId, className }: { cursusId: number; className?: string }) {
  const { data: bilan } = useQuery({
    queryKey: ["bilan-periode", cursusId, 7],
    queryFn: ({ signal }) => getBilanPeriode(cursusId, signal, 7),
    retry: false,
  })

  if (!bilan) return null
  const atteints = jalonsAtteints(bilan)
  const prochain = prochainJalon(bilan)
  const gain = gainDeTaux(bilan)
  if (!bilan.a_de_l_activite && atteints.length === 0) return null

  return (
    <div className={className}>
      <Ecrin variante="sobre" className="sm:p-6">
        <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-primary">
          <Sparkles className="size-3.5" />
          Ta semaine
        </p>

        <dl className="mt-3 grid grid-cols-3 gap-3">
          <Chiffre valeur={bilan.seances} unite={bilan.seances > 1 ? "séances" : "séance"} />
          <Chiffre valeur={bilan.questions} unite={bilan.questions > 1 ? "questions" : "question"} />
          <Chiffre
            valeur={bilan.taux_reussite === null ? "–" : `${bilan.taux_reussite} %`}
            unite="de réussite"
            note={gain !== null ? `+${gain} points` : undefined}
          />
        </dl>

        {atteints.length > 0 && (
          <ul className="mt-4 flex flex-col gap-2">
            {atteints.slice(0, 2).map((jalon) => (
              <li
                key={`${jalon.genre}-${jalon.palier}`}
                className="flex items-center gap-3 rounded-xl border border-gold/35 bg-gold/[0.08] px-3.5 py-2.5 text-sm"
              >
                <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-gold/25 text-gold-foreground dark:text-gold">
                  <Trophy className="size-4" />
                </span>
                <span className="min-w-0">
                  <span className="block text-xs font-semibold uppercase tracking-wide text-muted-foreground">Palier franchi</span>
                  <span className="block font-medium">{jalon.libelle}</span>
                </span>
              </li>
            ))}
          </ul>
        )}

        {prochain && (
          <div className="mt-4">
            <p className="flex items-center justify-between gap-3 text-sm text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <ArrowRight className="size-3.5 shrink-0" />
                Prochain palier
              </span>
              <span className="tabular-nums font-medium text-foreground">
                {prochain.actuel} / {prochain.palier}
              </span>
            </p>
            <p className="mt-0.5 pl-5 text-sm font-medium">{prochain.libelle}</p>
            <div
              className="mt-2 h-2 overflow-hidden rounded-full bg-muted"
              role="progressbar"
              aria-valuemin={0}
              aria-valuemax={prochain.palier}
              aria-valuenow={prochain.actuel}
              aria-label={prochain.libelle}
            >
              <div
                className="h-full rounded-full bg-gradient-to-r from-primary to-gold transition-[width] duration-700"
                style={{ width: `${Math.round(prochain.avancement * 100)}%` }}
              />
            </div>
          </div>
        )}
      </Ecrin>
    </div>
  )
}

/** Mêmes règles que le bilan mensuel : jamais une baisse, et un socle comparable des deux côtés. */
function gainDeTaux(bilan: BilanPeriode): number | null {
  if (bilan.taux_reussite === null || bilan.taux_avant === null || bilan.questions < 5) return null
  const gain = bilan.taux_reussite - bilan.taux_avant
  return gain > 0 ? gain : null
}

function Chiffre({ valeur, unite, note }: { valeur: number | string; unite: string; note?: string }) {
  return (
    <div>
      <dd className="font-display text-2xl font-semibold tabular-nums leading-none sm:text-3xl">{valeur}</dd>
      <dt className="mt-1 text-sm text-muted-foreground">{unite}</dt>
      {note && <p className="text-sm font-semibold text-success">{note}</p>}
    </div>
  )
}
