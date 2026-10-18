import { Link } from "react-router-dom"
import { ArrowDown, ArrowRight, Target } from "lucide-react"

import { DemoQuizQuestion } from "@/components/DemoQuizQuestion"
import { t, useI18n } from "@/lib/i18n"

/**
 * Ce qui vient APRÈS les quiz gratuits sur /quiz, pour qui n'a pas d'abonnement : le produit complet.
 *
 * Avant, cette suite était une carte de même poids que le reste de la page, sans transition : on sortait d'une
 * liste de quiz gratuits qui s'arrêtait net, et trois appels à l'action (« Essayer », « Se connecter »,
 * « Lancer une vraie séance ») se disputaient l'attention. Ici :
 *  - un séparateur annonce l'étape suivante (l'essai est l'échantillon, ceci est le produit) ;
 *  - un seul bloc, plein et coloré pour trancher sur le fond de la page, réunit l'argument, les trois étapes et
 *    la question d'exemple ;
 *  - un seul appel principal (créer un compte ; pour un inscrit sans abonnement, voir les prix), la connexion et
 *    les prix restant des liens secondaires.
 */
export function QuizCompletVisiteur({ connecte }: { connecte: boolean }) {
  useI18n()
  const lienCompte = { to: "/connexion", state: { from: "/quiz", intent: t("quiz.connexion_pour_lancer") } }
  const principal = connecte ? { to: "/tarifs", libelle: t("qd.complet_prix") } : { ...lienCompte, libelle: t("qd.complet_cta") }
  const etapes = [t("qd.etape1"), t("qd.etape2"), t("qd.etape3")]

  return (
    <section aria-labelledby="quiz-complet-titre" className="mt-10 sm:mt-12">
      {/* Transition : un trait, une pastille, un trait. Décoratif : le titre du bloc porte le sens. */}
      <div aria-hidden className="mb-5 flex items-center gap-3">
        <span className="h-px flex-1 bg-gradient-to-r from-transparent to-border" />
        <span className="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1.5 text-xs font-semibold uppercase tracking-[0.12em] text-primary">
          {t("qd.suite_transition")}
          <ArrowDown className="size-3.5" />
        </span>
        <span className="h-px flex-1 bg-gradient-to-l from-transparent to-border" />
      </div>

      <div className="relative overflow-hidden rounded-3xl bg-primary text-primary-foreground shadow-xl shadow-primary/20">
        <div
          aria-hidden
          className="absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, currentColor 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <Target
          aria-hidden
          className="pointer-events-none absolute -bottom-10 -left-8 hidden size-56 rotate-[12deg] text-primary-foreground/[0.07] lg:block"
        />

        <div className="relative grid gap-8 p-6 sm:p-9 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)] lg:items-center lg:gap-12">
          <div className="min-w-0">
            <p className="mb-2 font-display text-sm italic text-primary-foreground/80">{t("qd.complet_surtitre")}</p>
            <h2
              id="quiz-complet-titre"
              className="font-display text-2xl font-semibold leading-[1.15] tracking-tight text-balance sm:text-4xl"
            >
              {t("qd.complet_titre_debut")}{" "}
              <span className="underline decoration-primary-foreground/40 decoration-2 underline-offset-[6px]">
                {t("qd.complet_titre_accent")}
              </span>
              {t("qd.complet_titre_fin")}
            </h2>
            <p className="mt-3 max-w-xl text-primary-foreground/85">{t("qd.complet_texte")}</p>

            <ol aria-label={t("qd.complet_etapes")} className="mt-6 flex flex-col gap-3">
              {etapes.map((etape, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-primary-foreground/90">
                  <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-primary-foreground/15 text-xs font-semibold">
                    {i + 1}
                  </span>
                  <span className="pt-0.5">{etape}</span>
                </li>
              ))}
            </ol>

            <div className="mt-7 flex flex-col items-start gap-3">
              <Link
                to={principal.to}
                state={"state" in principal ? principal.state : undefined}
                className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-md bg-primary-foreground px-6 text-base font-semibold text-primary shadow-sm transition-colors hover:bg-primary-foreground/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-foreground focus-visible:ring-offset-2 focus-visible:ring-offset-primary sm:w-auto"
              >
                {principal.libelle}
                <ArrowRight className="size-4" />
              </Link>
              {!connecte && (
                <p className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-primary-foreground/85">
                  <Link {...lienCompte} className="underline underline-offset-4 hover:text-primary-foreground">
                    {t("qd.complet_deja")}
                  </Link>
                  <Link to="/tarifs" className="underline underline-offset-4 hover:text-primary-foreground">
                    {t("qd.complet_prix")}
                  </Link>
                </p>
              )}
            </div>
          </div>

          <aside className="min-w-0">
            <DemoQuizQuestion />
          </aside>
        </div>
      </div>
    </section>
  )
}
