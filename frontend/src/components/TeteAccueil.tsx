import { useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Check, ChevronDown, GraduationCap, Moon, Sparkles, Sun } from "lucide-react"

import { getPlanDuJour } from "@/api/endpoints"
import type { Accueil, CompteARebours, Cursus, PhaseExamen } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"
import { BoutonSimulation } from "@/components/BoutonSimulation"
import { formatCursus } from "@/components/CompteAReboursBadge"
import { LigneJour } from "@/components/LigneJour"
import { SeanceCorps } from "@/components/SeanceDuJour"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useCursusAbonnes } from "@/lib/changerCursusPrepare"
import { useChangerProfilActif } from "@/lib/changerProfilActif"
import { seanceAffichable } from "@/lib/seance"
import { trackEvent } from "@/lib/analytics"
import { themesFrequentsPath } from "@/lib/countryPath"
import { pourcent } from "@/lib/maitrise"
import { cn } from "@/lib/utils"

// Part de préparation (0-1) sous laquelle l'anneau n'est pas montré dans le bandeau.
const SEUIL_ANNEAU_VISIBLE = 0.1

/**
 * La tête de l'accueil d'un abonné : UNE carte, UNE action.
 *
 * Avant, un bandeau (compte à rebours, anneau) et la séance du jour étaient deux
 * cartes empilées avec chacune leur grand titre - sur téléphone, "Commencer" passait
 * sous le pli. Ici le bandeau devient la bande supérieure de la même carte : qui tu es
 * et où tu en es, une phrase de coach, et juste dessous le bouton.
 *
 * La phrase du coach vient du serveur (voir quiz.accueil.phrase_coach) : elle est
 * composée de faits déjà en base, jamais d'un slogan.
 *
 * Le corps dépend de la PHASE (voir quiz.accueil.phase_examen) : la séance le plus
 * souvent ; à un mois, une annale en conditions d'examen en action secondaire ; la
 * veille, une checklist et rien à découvrir ; le jour J, un mot et rien d'autre ; après,
 * une question - comment ça s'est passé ?
 */
export function TeteAccueil({ accueil, country }: { accueil: Accueil; country: string }) {
  const { user } = useAuth()
  // La séance vit sous la clé "plan-du-jour" comme partout (voir SeanceCorps : ses
  // mutations y écrivent). L'accueil agrégé l'y a déposée (voir AccueilEleve) ; ici on
  // ne refetche jamais de nous-mêmes (staleTime infini), on lit ce que les actions y
  // mettent - et le plan reçu sert de point de départ quand rien n'y est encore.
  const { data: plan } = useQuery({
    queryKey: ["plan-du-jour"],
    queryFn: ({ signal }) => getPlanDuJour(signal),
    staleTime: Infinity,
    initialData: accueil.plan,
  })
  const cursus = user?.cursus_prepare
  const compte = user?.compte_a_rebours ?? plan?.compte_a_rebours ?? null
  const prenom = (user?.profil_actif?.prenom || user?.pseudo || user?.full_name || "").trim().split(/\s+/)[0]
  // L'objectif d'XP du jour et la semaine : ce qui fait revenir. Ni le jour de l'examen
  // ni le lendemain n'ont de séance à tenir, donc rien à compter ces jours-là.
  const ligneJour =
    plan?.xp && plan.serie && accueil.phase !== "apres" && accueil.phase !== "jour_j"
      ? <LigneJour etat={plan.xp} serie={plan.serie} />
      : null
  const phraseSousLeTitre =
    plan?.etat === "plan_pret" && Boolean(plan.seance)
    && (accueil.phase === "normal" || accueil.phase === "simulation" || accueil.phase === "derniere_ligne_droite")
    && seanceAffichable(plan)
  const ligneSousLeBouton =
    Boolean(ligneJour) && accueil.phase !== "veille" && plan?.etat === "plan_pret"
    && Boolean(plan.seance) && !plan.seance?.verrouillee
  // La grande bande verte n'a de raison d'être que si elle porte quelque chose : un mot du
  // coach (séance faite, veille, jour J...), un vrai compte à rebours, ou l'anneau de
  // préparation. Avec une séance à faire et rien de tout cela - date seulement estimée -, il
  // ne restait que « Bonjour » et une date dans 85 à 125 px de vert : une ligne suffit.
  const anneauVisible = Boolean(accueil.preparation) && !accueil.premiers_pas
    && (accueil.preparation?.ponderee ?? 0) >= SEUIL_ANNEAU_VISIBLE
  const joursExacts = Boolean(compte) && !compte?.estimee && (compte?.jours_restants ?? 0) > 0
  const bandeFine = phraseSousLeTitre && !anneauVisible && !joursExacts

  return (
    <section className="mx-auto max-w-5xl px-4 pt-5 sm:px-6 sm:pt-6" aria-label="Aujourd'hui">
      <div className="animate-fade-up relative overflow-hidden rounded-3xl border border-primary/20 bg-card shadow-xl shadow-primary/[0.07]">
        {bandeFine && <BandeFine prenom={prenom} cursus={cursus} phase={accueil.phase} compte={compte} />}
        {/* La bande du coach : fond de marque, texte clair. Le dégradé reste au-dessus
            de 90 % de la couleur pleine pour que le blanc garde son contraste jusqu'au
            bord droit (le précédent bandeau descendait à 75 %). */}
        {!bandeFine && (
        <div className="relative bg-gradient-to-br from-primary via-primary to-primary/90 px-5 py-5 text-primary-foreground sm:px-8 sm:py-6">
          <div aria-hidden className="pointer-events-none absolute -right-16 -top-20 size-64 rounded-full bg-gold/25 blur-3xl" />
          <div aria-hidden className="pointer-events-none absolute -bottom-24 -left-10 size-56 rounded-full bg-white/10 blur-3xl" />
          <div className="relative flex items-start justify-between gap-5">
            <div className="min-w-0 flex-1">
              <p className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs font-semibold uppercase tracking-[0.18em] text-primary-foreground/80">
                <span>
                  {prenom ? `Bonjour ${prenom}` : "Bonjour"}
                  {cursus && <CursusPreparePuce cursus={cursus} />}
                </span>
                <BadgePhase phase={accueil.phase} />
              </p>
              <Decompte compte={compte} premiersPas={accueil.premiers_pas} />
              {/* Avec une séance à faire, la phrase du coach vit dans la carte, SOUS le titre
                  du thème (voir SeanceCorps) : dans la bande, elle parlait d'un « ce thème »
                  qu'on ne voyait pas, et la date d'examen, plus grosse, passait avant elle.
                  Les autres cas (séance faite, veille, jour J, après) gardent leur mot ici. */}
              {!phraseSousLeTitre && (
                // text-base sur téléphone : en text-lg, la phrase tenait sur six lignes et
                // repoussait "Commencer" à la limite du pli.
                <p className="mt-3 max-w-2xl font-display text-base font-medium leading-snug text-balance sm:text-xl">
                  {accueil.phrase_coach}
                </p>
              )}
              {/* Le compteur « N séances cette semaine » a disparu du bandeau : la semaine de
                  série (LigneJour, dans le corps de la carte) dit déjà quels jours ont compté. */}
            </div>
            {/* Pas d'anneau tant que rien n'est mesuré : un "0 %" le premier jour dit
                "tu n'as rien fait" à quelqu'un qui vient d'arriver. Il apparaît après la
                première séance - et "Où j'en suis", plus bas, garde le compte brut.
                À sa place, quand un vrai nombre de jours est connu (jamais sur une
                date estimée, voir Decompte), ce nombre migre ici plutôt que de
                laisser la moitié du bandeau vide : c'est le même repère - "le chiffre
                qui résume où j'en suis maintenant" - simplement fondé sur le compte à
                rebours plutôt que sur la maîtrise, qui n'existe pas encore. Et quand
                même ce chiffre n'existe pas (date encore estimée, ou pas d'examen
                déclaré), une illustration comble l'espace plutôt que de le laisser
                vide - voir IllustrationAujourdhui, volontairement en dernier recours :
                un vrai repère prime toujours sur la décoration quand il y en a un. */}
            {/* Sous SEUIL_ANNEAU_VISIBLE, un « 1 % » décourage plus qu'il n'informe : l'anneau
                attend d'avoir de quoi dire (« Où j'en suis », plus bas, montre le compte brut). */}
            {accueil.preparation && !accueil.premiers_pas && accueil.preparation.ponderee >= SEUIL_ANNEAU_VISIBLE ? (
              <AnneauPreparation part={accueil.preparation.ponderee} />
            ) : accueil.premiers_pas && compte && !compte.estimee && compte.jours_restants > 0 ? (
              <RepereJoursRestants compte={compte} />
            ) : accueil.premiers_pas ? (
              <IllustrationAujourdhui />
            ) : null}
          </div>
        </div>
        )}

        <div className="relative p-5 sm:p-8">
          {/* L'objectif du jour et la semaine : ce qui fait revenir. Ni le jour de l'examen
              ni le lendemain n'ont de séance à tenir, donc rien à compter ces jours-là. */}
          {/* Avec une séance à faire, la ligne passe SOUS le bouton et le choix de durée (voir
              Corps) : en tête de carte, elle prenait ~140 px et repoussait « Commencer » à la
              limite du pli sur un téléphone. Sans séance à faire, elle garde sa place. */}
          {ligneJour && !ligneSousLeBouton && ligneJour}
          <Corps accueil={accueil} plan={plan} country={country} ligneJour={ligneSousLeBouton ? ligneJour : undefined} />
        </div>
      </div>
    </section>
  )
}

function Corps({
  accueil, plan, country, ligneJour,
}: { accueil: Accueil; plan: Accueil["plan"] | undefined; country: string; ligneJour?: ReactNode }) {
  const { phase } = accueil
  if (phase === "apres") return <ApresExamen />
  if (phase === "jour_j") return <JourJ />
  if (phase === "veille") return <Veille plan={plan} country={country} />
  if (!plan) return null
  if (seanceAffichable(plan)) {
    return (
      <SeanceCorps
        plan={plan}
        country={country}
        phraseDuCoach={accueil.phrase_coach}
        apresDuree={ligneJour}
        secondaire={accueil.simulation_suggeree && plan.etat === "plan_pret" ? (
          <SimulationSuggeree suggestion={accueil.simulation_suggeree} />
        ) : undefined}
      />
    )
  }
  if (plan.etat === "rien_a_proposer") {
    return (
      <p className="text-sm text-muted-foreground">
        On n'a rien à te proposer aujourd'hui.{" "}
        <Link to={themesFrequentsPath(country)} className="underline underline-offset-4 hover:text-primary">
          Choisir un thème toi-même
        </Link>
      </p>
    )
  }
  return null
}

/**
 * "· BAC D" à côté de "Bonjour" - simple texte pour la plupart des comptes, mais
 * devient un sélecteur dès que deux abonnements ou plus sont actifs : c'est ici,
 * dans "Aujourd'hui", qu'on voit le plus vite qu'on regarde le mauvais examen, donc
 * c'est ici qu'il doit être le plus rapide d'en changer (voir aussi AccountMenu dans
 * Header.tsx, même mécanisme, pour qui préfère passer par le menu du compte).
 *
 * Chaque entrée est un ABONNEMENT (profil + cursus), pas un simple cursus : deux
 * profils peuvent préparer le même examen (voir useCursusAbonnes) - cliquer doit donc
 * basculer sur CE couple précis (activerProfil avec cursusId), jamais sur le cursus
 * seul, qui laisserait le profil actif inchangé et pourrait associer un enfant à un
 * cursus qui n'est pas le sien (régression signalée).
 */
function CursusPreparePuce({ cursus, clair = false }: { cursus: Cursus; clair?: boolean }) {
  const { user } = useAuth()
  const cursusAbonnes = useCursusAbonnes()
  const changerProfil = useChangerProfilActif()

  if (cursusAbonnes.length < 2 || user?.session_restreinte) {
    return <> · {formatCursus(cursus)}</>
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          // Une pastille plutôt qu'un texte : avec deux abonnements, savoir lequel on regarde
          // est la première chose à voir, et un « BEPC ⌄ » de 10 px ne se lisait pas comme un bouton.
          className={cn(
            "ml-1.5 inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[0.7rem] normal-case tracking-normal transition-colors",
            clair
              ? "bg-primary/10 text-primary hover:bg-primary/20"
              : "bg-white/15 text-primary-foreground hover:bg-white/25",
          )}
        >
          {formatCursus(cursus)}
          <ChevronDown className="size-3.5" aria-hidden="true" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        {cursusAbonnes.map((sub) => {
          const actif = sub.cursus.id === cursus.id && sub.profil.id === user?.profil_actif?.id
          return (
            <DropdownMenuItem
              key={sub.id}
              disabled={changerProfil.isPending}
              onSelect={() => {
                if (!actif) changerProfil.mutate({ profilId: sub.profil.id, cursusId: sub.cursus.id, prenom: sub.profil.prenom })
              }}
            >
              {actif ? <Check className="text-primary" /> : <GraduationCap />}
              {formatCursus(sub.cursus)} ({sub.profil.prenom})
            </DropdownMenuItem>
          )
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

/** Un mot sur la phase quand elle change quelque chose à la page - jamais en temps normal. */
function BadgePhase({ phase, clair = false }: { phase: PhaseExamen; clair?: boolean }) {
  const libelle =
    phase === "simulation" ? "Mois des annales"
    : phase === "derniere_ligne_droite" ? "Dernière ligne droite"
    : phase === "veille" ? "C'est demain"
    : null
  if (!libelle) return null
  return (
    <span
      className={cn(
        "rounded-full px-2 py-0.5 text-[0.65rem] normal-case tracking-normal",
        clair ? "bg-primary/10 text-primary" : "bg-white/15",
      )}
    >
      {libelle}
    </span>
  )
}

/** « mai 2027 » : le mois d'une date d'examen seulement estimée (voir Decompte). */
function moisEstime(compte: CompteARebours): string {
  const [annee, mois] = compte.date_examen.split("-").map(Number)
  const nomMois = new Intl.DateTimeFormat("fr-FR", { month: "long" }).format(new Date(annee, mois - 1, 15))
  return `${nomMois} ${annee}`
}

/**
 * La bande réduite à une ligne : « Bonjour Serge · BAC D », la phase si elle compte, et la
 * date d'examen quand elle n'est qu'estimée. Remplace le grand bloc vert quand celui-ci n'aurait
 * rien d'autre à porter (voir `bandeFine` dans TeteAccueil).
 *
 * La date est masquée dès `sm` : l'en-tête de la page affiche déjà « BAC D · vers mai 2027 »
 * à partir de cette largeur (voir Header), et la redire ici ne ferait que doubler le repère.
 */
function BandeFine({
  prenom, cursus, phase, compte,
}: { prenom: string; cursus: Cursus | null | undefined; phase: PhaseExamen; compte: CompteARebours | null }) {
  const dateEstimee = compte && compte.estimee && compte.jours_restants >= 0 ? moisEstime(compte) : null
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1 border-b border-primary/10 bg-primary/[0.06] px-5 py-2.5 text-xs font-semibold uppercase tracking-[0.18em] text-primary sm:px-8">
      <p className="flex flex-wrap items-center gap-x-2 gap-y-1">
        <span>
          {prenom ? `Bonjour ${prenom}` : "Bonjour"}
          {cursus && <CursusPreparePuce cursus={cursus} clair />}
        </span>
        <BadgePhase phase={phase} clair />
      </p>
      {dateEstimee && (
        <span className="font-medium normal-case tracking-normal text-muted-foreground sm:hidden">
          Examen vers {dateEstimee}
        </span>
      )}
    </div>
  )
}

/**
 * Le compte à rebours, sur une ligne : le chiffre en grand mais plus en 6xl - il
 * n'est plus la vedette de la carte, la phrase et le bouton le sont. Même règle que
 * CompteAReboursBadge : jamais de rouge, jamais d'alarme.
 *
 * `premiersPas` : au tout premier passage, avec une date d'examen connue (pas
 * estimée), le nombre de jours migre dans l'espace de l'anneau (voir
 * RepereJoursRestants) plutôt que de rester ici - jamais les deux à la fois, ce
 * serait le même fait redit deux fois dans la même bande.
 */
function Decompte({ compte, premiersPas }: { compte: CompteARebours | null; premiersPas: boolean }) {
  if (!compte || compte.jours_restants < 0) return null
  if (compte.estimee) {
    const [annee, mois] = compte.date_examen.split("-").map(Number)
    const nomMois = new Intl.DateTimeFormat("fr-FR", { month: "long" }).format(new Date(annee, mois - 1, 15))
    return (
      // Plus petit sur téléphone : une date seulement estimée n'appelle aucune action, elle
      // ne doit pas dominer la bande, ni passer devant le thème du jour.
      <p className="mt-1.5 font-display text-lg font-semibold leading-tight sm:text-2xl">
        Examen vers {nomMois} {annee}
      </p>
    )
  }
  if (compte.jours_restants === 0) {
    return <p className="mt-1.5 font-display text-2xl font-semibold leading-tight sm:text-3xl">C'est aujourd'hui</p>
  }
  if (premiersPas) return null
  const [annee, mois, jour] = compte.date_examen.split("-").map(Number)
  const date = new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "long" }).format(new Date(annee, mois - 1, jour))
  return (
    <p className="mt-1.5 flex flex-wrap items-baseline gap-x-2 font-display leading-none">
      <span className="text-4xl font-semibold tabular-nums sm:text-5xl">{compte.jours_restants}</span>
      <span className="text-base font-medium text-primary-foreground/85 sm:text-lg">
        jour{compte.jours_restants > 1 ? "s" : ""} avant l'examen
      </span>
      <span className="text-sm text-primary-foreground/70">· {compte.session_label}, le {date}</span>
    </p>
  )
}

/**
 * Le nombre de jours restants, dans l'espace de l'anneau - pour le tout premier
 * passage d'un élève dont la date d'examen est connue avec certitude.
 *
 * Jamais une illustration : ce chiffre est déjà en base, déjà calculé, déjà digne de
 * confiance (voir ExamSession.compte_a_rebours_pour) - le montrer ici ne fait que lui
 * donner la place qu'occupera l'anneau de maîtrise dès la première séance terminée.
 * Pas de cercle autour : un anneau plein tromperait ("t'es prêt à 100 %"), un anneau
 * vide découragerait sans rien mesurer - seul le chiffre, honnête sur ce qu'il dit.
 */
function RepereJoursRestants({ compte }: { compte: CompteARebours }) {
  return (
    <div className="flex size-20 shrink-0 flex-col items-center justify-center text-center leading-tight sm:size-28">
      <span className="font-display text-3xl font-semibold tabular-nums sm:text-4xl">{compte.jours_restants}</span>
      <span className="mt-1 text-[0.65rem] text-primary-foreground/80 sm:text-xs">
        jour{compte.jours_restants > 1 ? "s" : ""} avant l'examen
      </span>
    </div>
  )
}

/**
 * Le dernier recours de l'espace de l'anneau : quand ni la maîtrise ni un nombre de
 * jours fiable n'existent encore (date d'examen estimée, ou pas d'examen déclaré du
 * tout), rien de vrai ne peut s'y afficher - alors plutôt qu'un vide, une
 * illustration, un seul trait, dans les teintes mêmes du bandeau plutôt qu'une
 * couleur ou une scène qui détonnerait. Purement décorative : `aria-hidden`, rien
 * qu'un lecteur d'écran aurait à annoncer.
 */
function IllustrationAujourdhui() {
  return (
    // Absente sur téléphone : purement décorative, elle réduisait la phrase du coach à la
    // moitié de la largeur (cinq lignes) et repoussait le bouton sous le pli.
    <div aria-hidden="true" className="hidden size-20 shrink-0 items-center justify-center sm:flex sm:size-28">
      <GraduationCap className="size-12 text-primary-foreground/25 sm:size-16" strokeWidth={1.25} />
    </div>
  )
}

/** L'anneau pondéré : la part de ce qui tombe vraiment à l'examen (voir
 * quiz.accueil.preparation), trait clair sur fond de marque. */
function AnneauPreparation({ part }: { part: number }) {
  const rayon = 30
  const circonference = 2 * Math.PI * rayon
  return (
    <div
      className="relative size-20 shrink-0 sm:size-28"
      role="img"
      aria-label={`${pourcent(part)} % de ce qui tombe à l'examen est maîtrisé`}
    >
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
        <span className="font-display text-xl font-semibold tabular-nums sm:text-3xl">
          {pourcent(part)}<span className="text-sm">%</span>
        </span>
        <span className="text-[0.6rem] text-primary-foreground/80 sm:text-[0.65rem]">de l'essentiel</span>
      </span>
    </div>
  )
}

/**
 * À un mois : l'annale suggérée par le serveur (matière qui pèse le plus, session la
 * plus récente, jamais déjà simulée - voir quiz.accueil.simulation_suggeree), en action
 * secondaire à côté de "Commencer". Le titre dit laquelle, pour que le bouton ne soit
 * pas une promesse en l'air.
 */
function SimulationSuggeree({ suggestion }: { suggestion: NonNullable<Accueil["simulation_suggeree"]> }) {
  return (
    <>
      <BoutonSimulation epreuveId={suggestion.id} />
      <p className="basis-full text-xs text-muted-foreground">
        Annale suggérée : {suggestion.subject_label}{suggestion.year ? ` ${suggestion.year}` : ""} · {suggestion.title}
      </p>
    </>
  )
}

const CHECKLIST_VEILLE = [
  "Convocation et pièce d'identité dans le sac",
  "Stylos, règle, et la calculatrice si elle est autorisée",
  "Une montre : le téléphone reste dehors",
  "Le trajet et l'heure d'arrivée vérifiés",
  "Coucher tôt : une nuit complète vaut plus qu'une dernière relecture",
]

/**
 * La veille : rien à apprendre, une liste à cocher, et une relecture courte pour qui
 * y tient. Les coches vivent dans le navigateur (localStorage) : ce sont les siennes,
 * elles ne servent à rien d'autre.
 */
function Veille({ plan, country }: { plan: Accueil["plan"] | undefined; country: string }) {
  const cle = "edukora:veille:coches"
  const [coches, setCoches] = useState<boolean[]>(() => {
    try {
      const brut = localStorage.getItem(cle)
      const lu = brut ? (JSON.parse(brut) as boolean[]) : []
      return CHECKLIST_VEILLE.map((_, i) => Boolean(lu[i]))
    } catch {
      return CHECKLIST_VEILLE.map(() => false)
    }
  })
  const [relire, setRelire] = useState(false)

  function basculer(index: number) {
    const suivantes = coches.map((c, i) => (i === index ? !c : c))
    setCoches(suivantes)
    try {
      localStorage.setItem(cle, JSON.stringify(suivantes))
    } catch {
      // Sans stockage, les coches vivent le temps de la page.
    }
  }

  return (
    <div>
      <h2 className="flex items-center gap-2 font-display text-2xl font-semibold sm:text-3xl">
        <Moon className="size-5 shrink-0 text-primary" aria-hidden="true" />
        Ce soir, on prépare le sac
      </h2>
      <ul className="mt-4 flex flex-col gap-2">
        {CHECKLIST_VEILLE.map((item, index) => (
          <li key={item}>
            <button
              type="button"
              onClick={() => basculer(index)}
              aria-pressed={coches[index]}
              className={cn(
                "flex w-full items-center gap-3 rounded-xl border px-3.5 py-2.5 text-left text-sm transition-colors",
                coches[index]
                  ? "border-primary/30 bg-primary/5 text-muted-foreground line-through"
                  : "border-border bg-background hover:border-primary/40",
              )}
            >
              <span
                className={cn(
                  "flex size-5 shrink-0 items-center justify-center rounded-md border",
                  coches[index] ? "border-primary bg-primary text-primary-foreground" : "border-border",
                )}
              >
                {coches[index] && <Check className="size-3.5" strokeWidth={3} />}
              </span>
              {item}
            </button>
          </li>
        ))}
      </ul>
      {plan && seanceAffichable(plan) && plan.etat === "plan_pret" && (
        <div className="mt-5">
          {relire ? (
            <div className="border-t border-border/60 pt-5">
              <SeanceCorps plan={plan} country={country} />
            </div>
          ) : (
            <Button variant="ghost" size="sm" className="rounded-full text-muted-foreground" onClick={() => setRelire(true)}>
              Relire dix minutes quand même
            </Button>
          )}
        </div>
      )}
    </div>
  )
}

/** Le jour J : un mot, trois repères, et surtout pas de séance. */
function JourJ() {
  return (
    <div>
      <h2 className="flex items-center gap-2 font-display text-2xl font-semibold sm:text-3xl">
        <Sun className="size-5 shrink-0 text-gold-text" aria-hidden="true" />
        Bonne chance
      </h2>
      <ul className="mt-4 flex flex-col gap-2 text-sm text-muted-foreground">
        <li className="flex items-start gap-2"><Check className="mt-0.5 size-4 shrink-0 text-primary" />Lis chaque consigne deux fois avant d'écrire.</li>
        <li className="flex items-start gap-2"><Check className="mt-0.5 size-4 shrink-0 text-primary" />Commence par ce que tu sais faire : les points faciles d'abord.</li>
        <li className="flex items-start gap-2"><Check className="mt-0.5 size-4 shrink-0 text-primary" />Garde cinq minutes à la fin pour relire.</li>
      </ul>
    </div>
  )
}

const RESSENTIS = [
  { code: "bien", libelle: "Plutôt bien" },
  { code: "moyen", libelle: "Mitigé" },
  { code: "difficile", libelle: "Difficile" },
] as const

/**
 * Après l'examen : on arrête tout et on demande. La réponse part en analytics (voir
 * EventName.EXAMEN_RESSENTI) - le seul retour qu'on ait sur ce que valait la
 * préparation - et n'est demandée qu'une fois (mémoire du navigateur).
 */
function ApresExamen() {
  const cle = "edukora:examen:ressenti"
  const [repondu, setRepondu] = useState<string | null>(() => {
    try {
      return localStorage.getItem(cle)
    } catch {
      return null
    }
  })

  function repondre(code: string) {
    trackEvent("examen_ressenti", { ressenti: code })
    setRepondu(code)
    try {
      localStorage.setItem(cle, code)
    } catch {
      // Rien à faire.
    }
  }

  return (
    <div>
      <h2 className="flex items-center gap-2 font-display text-2xl font-semibold sm:text-3xl">
        <Sparkles className="size-5 shrink-0 text-primary" aria-hidden="true" />
        {repondu ? "Merci" : "Comment ça s'est passé ?"}
      </h2>
      {repondu ? (
        <p className="mt-3 text-sm text-muted-foreground">
          Tes corrigés, cours et quiz restent ouverts jusqu'à la fin de ton accès. Si tu prépares un autre examen,{" "}
          <Link to="/compte" className="underline underline-offset-4 hover:text-primary">dis-le nous</Link>.
        </p>
      ) : (
        <>
          <p className="mt-3 text-sm text-muted-foreground">Un mot suffit. Ça nous aide à mieux préparer les suivants.</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {RESSENTIS.map((r) => (
              <Button key={r.code} variant="outline" className="rounded-full" onClick={() => repondre(r.code)}>
                {r.libelle}
              </Button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
