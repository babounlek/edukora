import { Link } from "react-router-dom"
import { ArrowLeft, ArrowRight, Check, Lock } from "lucide-react"

import type { Cursus } from "@/api/types"
import { Button } from "@/components/ui/button"
import { ParrainageHint } from "@/components/ParrainageHint"
import { lienAbonnement } from "@/lib/retourAchat"

const AVANTAGES = [
  "Corrigés détaillés, pas à pas",
  "Cours et rappels de méthode liés",
  "Quiz et suivi de ta progression",
]

/**
 * Ce que voit un élève sans abonnement devant un contenu verrouillé (lecteur d'une épreuve ou
 * d'un cours, réponse 403) : une proposition, pas un message d'erreur. Le bouton mène droit au
 * paiement du cursus concerné, avec `retour` pour revenir lire le contenu dès que c'est payé.
 *
 * `cursus` vient de la requête publique de la page (vide tant qu'elle charge ou si elle a
 * échoué) : sans cursus connu on renvoie vers les formules plutôt que de proposer un achat
 * sur un cursus au hasard.
 */
export function AccesRefuse({
  cursus,
  retour,
  nature,
  liens,
}: {
  cursus: Cursus[]
  retour: string
  nature: "épreuve" | "cours"
  liens: { to: string; label: string }[]
}) {
  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6 sm:py-16">
      <section className="relative overflow-hidden rounded-3xl border border-primary/25 bg-gradient-to-br from-primary/[0.08] via-primary/[0.03] to-gold/[0.06] p-6 text-center shadow-lg shadow-primary/5 sm:p-9">
        <div
          className="pointer-events-none absolute -right-16 -top-16 size-56 rounded-full bg-gold/10 blur-3xl"
          aria-hidden="true"
        />
        <div className="relative">
          <span className="mx-auto mb-4 flex size-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Lock className="size-7" aria-hidden="true" />
          </span>
          <h1 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
            Ce {nature === "cours" ? "cours" : "corrigé"} est réservé aux abonnés
          </h1>
          <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
            Un seul abonnement, valable jusqu'à ton examen, et tout s'ouvre : tu peux commencer à lire dès la
            confirmation du paiement.
          </p>

          <ul className="mx-auto mt-6 grid max-w-md gap-2 text-left">
            {AVANTAGES.map((avantage) => (
              <li key={avantage} className="flex items-start gap-2 rounded-xl bg-background/70 px-3 py-2.5 text-sm">
                <Check className="mt-0.5 size-4 shrink-0 text-primary" strokeWidth={3} aria-hidden="true" />
                {avantage}
              </li>
            ))}
          </ul>

          <div className="mt-7 flex flex-wrap justify-center gap-2">
            {cursus.length > 0 ? (
              cursus.map((c) => (
                <Button key={c.id} asChild size="lg" className="h-12 rounded-full px-6 shadow-lg shadow-primary/25">
                  <Link to={lienAbonnement(c.id, retour)}>
                    S'abonner{cursus.length > 1 ? ` (${c.series ? c.series.code : c.examen_display})` : ""}
                    <ArrowRight />
                  </Link>
                </Button>
              ))
            ) : (
              <Button asChild size="lg" className="h-12 rounded-full px-6 shadow-lg shadow-primary/25">
                <Link to="/tarifs">
                  Voir les formules
                  <ArrowRight />
                </Link>
              </Button>
            )}
          </div>

          <div className="mt-4 flex justify-center">
            <ParrainageHint />
          </div>
        </div>
      </section>

      <nav className="mt-6 flex flex-wrap items-center justify-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
        {liens.map((lien) => (
          <Link key={lien.to} to={lien.to} className="inline-flex items-center gap-1.5 hover:text-primary">
            <ArrowLeft className="size-4" aria-hidden="true" />
            {lien.label}
          </Link>
        ))}
      </nav>
    </div>
  )
}
