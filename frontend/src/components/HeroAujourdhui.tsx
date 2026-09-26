import type { CompteARebours } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { pourcent } from "@/lib/maitrise"
import { formatCursus } from "@/components/CompteAReboursBadge"

/**
 * L'en-tête de l'accueil d'un élève : où il en est vis-à-vis de SON examen, en un coup
 * d'œil - le compte à rebours en grand, et l'anneau de préparation.
 *
 * Le décompte reste neutre (même règle que CompteAReboursBadge : jamais de rouge, jamais
 * d'alarme) - il donne un ordre de marche, pas de l'angoisse. Et l'anneau ne dit que ce
 * qui est mesuré : la part des savoirs du programme réellement maîtrisés.
 *
 * Silencieusement absent sans cursus déclaré : un bandeau sans examen n'aurait rien à dire.
 */
export function HeroAujourdhui({
  preparation, seancesSemaine,
}: { preparation: number | null; seancesSemaine?: number }) {
  const { user } = useAuth()
  const cursus = user?.cursus_prepare
  if (!cursus) return null

  const compte = user?.compte_a_rebours ?? null
  const prenom = (user?.pseudo || user?.full_name || "").trim().split(/\s+/)[0]

  return (
    <section className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary via-primary to-primary/75 p-5 text-primary-foreground shadow-xl shadow-primary/20 sm:p-7">
        <div aria-hidden className="pointer-events-none absolute -right-16 -top-20 size-64 rounded-full bg-gold/25 blur-3xl" />
        <div aria-hidden className="pointer-events-none absolute -bottom-24 -left-10 size-56 rounded-full bg-white/10 blur-3xl" />

        <div className="relative flex items-center justify-between gap-5">
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary-foreground/75">
              {prenom ? `Bonjour ${prenom} · ` : ""}
              {formatCursus(cursus)}
            </p>
            <Decompte compte={compte} />
            {typeof seancesSemaine === "number" && seancesSemaine > 0 && (
              <p className="mt-2 text-sm text-primary-foreground/80">
                {seancesSemaine} séance{seancesSemaine > 1 ? "s" : ""} cette semaine
              </p>
            )}
          </div>
          {preparation !== null && <AnneauPreparation part={preparation} />}
        </div>
      </div>
    </section>
  )
}

function Decompte({ compte }: { compte: CompteARebours | null }) {
  if (!compte || compte.jours_restants < 0) {
    return <p className="mt-2 font-display text-2xl font-semibold leading-tight sm:text-3xl">Ta préparation</p>
  }
  // Date estimée : jamais un nombre de jours précis sur une date qu'on a nous-mêmes décalée
  // (voir ExamSession.compte_a_rebours_pour) - on dit le mois.
  if (compte.estimee) {
    const [annee, mois] = compte.date_examen.split("-").map(Number)
    const nomMois = new Intl.DateTimeFormat("fr-FR", { month: "long" }).format(new Date(annee, mois - 1, 15))
    return (
      <p className="mt-2 font-display text-2xl font-semibold leading-tight sm:text-3xl">
        Examen vers {nomMois} {annee}
      </p>
    )
  }
  if (compte.jours_restants === 0) {
    return <p className="mt-2 font-display text-3xl font-semibold leading-tight">C'est aujourd'hui</p>
  }
  return (
    <p className="mt-2 font-display leading-none">
      <span className="block text-6xl font-semibold tabular-nums">{compte.jours_restants}</span>
      <span className="mt-1.5 block text-base font-medium text-primary-foreground/85 sm:text-lg">
        jour{compte.jours_restants > 1 ? "s" : ""} avant l'examen
      </span>
    </p>
  )
}

/** L'anneau du hero : trait clair sur fond de marque - AnneauProgression (trait de marque
 * sur fond de carte) y serait invisible. */
function AnneauPreparation({ part }: { part: number }) {
  const rayon = 30
  const circonference = 2 * Math.PI * rayon
  return (
    <div className="relative size-24 shrink-0 sm:size-28" role="img" aria-label={`${pourcent(part)} % du programme maîtrisé`}>
      <svg viewBox="0 0 72 72" className="size-full -rotate-90">
        <circle cx="36" cy="36" r={rayon} fill="none" strokeWidth="6" className="stroke-primary-foreground/20" />
        <circle
          cx="36" cy="36" r={rayon} fill="none" strokeWidth="6" strokeLinecap="round"
          className="stroke-primary-foreground transition-[stroke-dashoffset] duration-1000"
          strokeDasharray={circonference}
          strokeDashoffset={circonference * (1 - Math.min(1, part))}
          opacity={part > 0 ? 1 : 0}
        />
      </svg>
      <span className="absolute inset-0 flex flex-col items-center justify-center leading-tight">
        <span className="font-display text-2xl font-semibold tabular-nums sm:text-3xl">{pourcent(part)}<span className="text-sm">%</span></span>
        <span className="text-xs text-primary-foreground/80">préparé</span>
      </span>
    </div>
  )
}
