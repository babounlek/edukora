import { useEffect, type ReactNode } from "react"
import { Link, Navigate, useParams, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, BookOpen, Clock, Crown, GraduationCap, Layers, Target, TrendingUp } from "lucide-react"

import heroStudent from "@/assets/hero-student.jpg"
import {
  getEpreuveInedite,
  getMyProgression,
  listCours,
  listCursus,
  listEpreuves,
  listSubjects,
  readEpreuve,
} from "@/api/endpoints"
import { trackEvent } from "@/lib/analytics"
import { examCodesFor, examLevelsFor, joinExamLevelsFr } from "@/lib/cursus"
import { useSeo } from "@/lib/seo"
import {
  epreuveInediteDetailPath,
  epreuveReaderPath,
  epreuvesListPath,
  themesFrequentsPath,
} from "@/lib/countryPath"
import { cn, formatAmount } from "@/lib/utils"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Button } from "@/components/ui/button"
import { SocialProofSection } from "@/components/SocialProofSection"
import { SeanceDuJour } from "@/components/SeanceDuJour"
import { AccueilEleve } from "@/components/AccueilEleve"
import { requeteInedites, useCursusAccueil, useInedites } from "@/lib/cursusAccueil"

// Épreuve gratuite dont le premier exercice sert d'exemple de "corrigé pas à pas"
// dans le hero (voir plus bas) - un vrai extrait de la base, pas un mock. Un seul
// pays ouvert au lancement (voir OnboardingModal.tsx) : le jour où un deuxième pays
// a du contenu, cette section devra choisir un slug par pays plutôt qu'un seul fixe.
const EXEMPLE_CORRIGE_SLUG = "mathematiques-bepc-2026"

// Clés de filtre reconnues par /epreuves (voir EpreuvesListPage) - un lien déjà en
// circulation qui les porte encore sur cette URL (recherche sauvegardée en session,
// lien partagé, l'onboarding qui pointait ici avant la scission accueil/catalogue)
// doit continuer à filtrer, pas silencieusement retomber sur l'accueil nu.
const FILTER_PARAM_KEYS = ["subject", "cursus", "origine", "nature", "gratuit", "search"]

/** Chiffre de volumétrie du hero - même gabarit de puce que /epreuves, /quiz et /cours. */
function StatChip({ icon, valeur, libelle }: { icon: ReactNode; valeur: string; libelle: string }) {
  return (
    <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
      {icon}
      <span className="font-medium tabular-nums">{valeur}</span>
      <span className="text-muted-foreground">{libelle}</span>
    </span>
  )
}


/** Une étape du récit "Comment ça marche" - raconte ce que la plateforme fait POUR
 * l'élève, là où la grille précédente listait les rayons qu'il devait parcourir lui-même. */
function EtapeExplication({ numero, titre, description }: { numero: string; titre: string; description: string }) {
  return (
    <div className="flex flex-col gap-2 rounded-2xl border border-border bg-card p-5">
      <span className="flex size-8 items-center justify-center rounded-full bg-primary/10 font-display font-semibold text-primary">
        {numero}
      </span>
      <h3 className="font-display text-lg font-semibold">{titre}</h3>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  )
}

/**
 * La page vitrine : le hero, les chiffres, l'exemple de corrigé, les inédites, la
 * preuve sociale. Ce que voient un visiteur anonyme, un robot d'indexation, et un
 * élève qui n'a pas encore d'abonnement - c'est pour ce dernier sa page de
 * conversion, la lui retirer coûterait des abonnements.
 *
 * Un élève ABONNÉ voit AccueilEleve à la place (voir CataloguePage en bas de
 * fichier) : plus aucun argumentaire, seulement ses affaires.
 */
function CatalogueVitrine() {
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = countries.find((c) => c.code.toLowerCase() === country)?.label
  const { isAuthenticated, user } = useAuth()
  const [searchParams] = useSearchParams()

  // Un élève qui a dit ce qu'il prépare n'a pas à se le voir redemander sur la même
  // page que son compte à rebours - voir la section "Qu'est-ce que tu prépares ?" et
  // les boutons du hero, qui s'adressent tous deux à quelqu'un qui n'a pas encore
  // répondu.
  const aDeclareSonExamen = isAuthenticated && Boolean(user?.cursus_prepare)

  // Un lien encore en circulation vers l'ancien catalogue-sur-l'accueil (ex.
  // "/cm?cursus=12", posé par l'onboarding ou une recherche sauvegardée avant la
  // scission accueil/catalogue) doit continuer à filtrer plutôt que d'atterrir sur un
  // hero qui ignore silencieusement ces paramètres.
  const hasLegacyFilters = FILTER_PARAM_KEYS.some((key) => searchParams.has(key))

  useEffect(() => {
    // ?ref=pdf_fiche_sujet : posé par le PDF énoncé d'une fiche répétiteur (voir
    // backend fiches.pdf._sujet_deep_link) sur son propre CTA - ce PDF circule auprès
    // des élèves du répétiteur, jamais encore inscrits sur edukora à ce stade, donc son
    // point d'atterrissage est bien l'accueil public (avec sa promesse et ses CTA),
    // pas directement le moteur de recherche. Seule façon de mesurer combien de
    // visites viennent réellement d'une fiche imprimée/partagée hors plateforme.
    if (searchParams.get("ref") !== "pdf_fiche_sujet") return
    trackEvent("pdf_fiche_sujet_landing", { country })
  }, [searchParams, country])

  // "Reprendre ma lecture" - jusqu'ici uniquement visible sur /compte, où un
  // utilisateur qui revient doit activement penser à aller la chercher. Ici c'est
  // silencieusement absent (pas d'erreur affichée) pour un visiteur anonyme ou sans
  // historique : ce n'est qu'un raccourci, jamais un contenu qu'on impose de voir.
  const { data: progressionData } = useQuery({
    queryKey: ["progression"],
    queryFn: ({ signal }) => getMyProgression(signal),
    enabled: isAuthenticated,
  })
  // `enabled: false` laisse le cache d'une session précédente intact plutôt que de le
  // vider - sans ce garde, une déconnexion sans rechargement complet de page
  // continuerait d'afficher "Reprendre : ..." avec la progression de l'utilisateur
  // précédent.
  const progression = isAuthenticated ? progressionData : undefined

  const { data: subjects = [] } = useQuery({
    queryKey: ["subjects", country],
    queryFn: ({ signal }) => listSubjects(country, signal),
  })

  const { data: cursusList = [] } = useQuery({
    queryKey: ["cursus", country],
    queryFn: ({ signal }) => listCursus(country, signal),
  })

  // Extrait réel d'un corrigé, pour la section "preuve" du hero (voir plus bas) - la
  // promesse du H1 ("la méthode qui t'apprend à réussir") doit se montrer, pas
  // seulement s'affirmer. `retry: false` : un 404 (slug renommé/retiré) doit faire
  // disparaître la section silencieusement, pas insister avec des tentatives inutiles.
  const { data: exempleContent } = useQuery({
    queryKey: ["epreuve-exemple-corrige", EXEMPLE_CORRIGE_SLUG],
    queryFn: () => readEpreuve(EXEMPLE_CORRIGE_SLUG),
    enabled: !hasLegacyFilters,
    retry: false,
  })
  const exempleExercice = exempleContent?.exercises[0]
  // Corrigé de la seule question 1, jamais l'exercice entier : corrige_markdown
  // concatène toutes les sous-questions sans séparateur explicite, et il commence
  // déjà par l'énoncé de la question 1 lui-même - une section "Énoncé" séparée le
  // répéterait. On coupe juste avant l'énoncé de la question 2, retrouvé verbatim
  // dans le corrigé (même technique de correspondance par chaîne exacte que
  // catalog.rendering.annotate_cours_links côté backend pour les liens vers les
  // cours) - repli sur le corrigé entier si l'exercice n'a qu'une question, ou si ce
  // texte ne s'y retrouve pas tel quel.
  const exempleSecondeSousQuestion = exempleExercice?.enonce_markdown.split("\n\n")[1]
  const exempleCorrigeQ1 = exempleExercice && (() => {
    if (!exempleSecondeSousQuestion) return exempleExercice.corrige_markdown
    const coupure = exempleExercice.corrige_markdown.indexOf(exempleSecondeSousQuestion)
    return coupure > 0 ? exempleExercice.corrige_markdown.slice(0, coupure).trim() : exempleExercice.corrige_markdown
  })()

  // Volume de cours du pays, pour la puce du hero et la carte "Cours" - même clé de
  // cache que /cours (voir CoursListPage), donc un aller-retour entre les deux pages
  // ne repaie pas la requête.
  const { data: coursData } = useQuery({
    queryKey: ["cours-total", country],
    queryFn: ({ signal }) => listCours({ country }, signal),
    enabled: Boolean(country) && !hasLegacyFilters,
  })

  // Volumétrie totale d'épreuves annoncée par le hero - même clé de cache que sur
  // /epreuves (voir EpreuvesListPage), donc un aller-retour entre les deux pages ne
  // repaie pas la requête.
  const { data: epreuvesTotalData } = useQuery({
    queryKey: ["epreuves-total", country],
    queryFn: ({ signal }) => listEpreuves({ country }, signal),
    enabled: Boolean(country) && !hasLegacyFilters,
  })
  const epreuvesTotal = epreuvesTotalData?.count

  // Épreuve inédite mise en avant, pour la section "preuve" dédiée plus bas - jamais un
  // slug codé en dur (contrairement à EXEMPLE_CORRIGE_SLUG) : la plus récente pour ce
  // pays, redécouverte à chaque chargement, donc jamais périmée si le contenu change.
  // Restreinte au cursus déclaré (compte ou onboarding) quand il y en a un : voir
  // useInedites.
  const cursusAccueil = useCursusAccueil(country ?? "")
  const { data: inediteRecenteData } = useInedites(country ?? "", cursusAccueil, !hasLegacyFilters)
  const inediteVedetteId = inediteRecenteData?.results[0]?.slug ?? inediteRecenteData?.results[0]?.id

  // Fiche complète de cette même épreuve : apercu_enonce_markdown (l'unique question
  // publique) n'est jamais renseigné sur le catalogue fusionné ci-dessus, seulement sur
  // la fiche détail (voir Epreuve.apercu_enonce_markdown côté types.ts). `retry: false` :
  // une inédite sans aperçu public ne doit pas se substituer silencieusement par une
  // autre. `isLoading` sert uniquement à retarder le repli compact (voir plus bas) le
  // temps de savoir si un aperçu existe - sans lui, ce repli clignoterait une fraction
  // de seconde avant que l'encart complet ne le remplace.
  const { data: inediteVedette, isLoading: inediteVedetteLoading } = useQuery({
    queryKey: ["epreuve-inedite-vedette", inediteVedetteId],
    queryFn: () => getEpreuveInedite(String(inediteVedetteId)),
    enabled: Boolean(inediteVedetteId) && !hasLegacyFilters,
    retry: false,
  })

  // Niveaux d'examen réellement présents pour ce pays (voir examLevelsFor) - jamais un
  // texte fixe : la plupart des pays n'ont pas de Probatoire. Repli générique tant que
  // cursusList n'a pas encore chargé, pour éviter un flash vide au premier rendu.
  const examLevels = examLevelsFor(cursusList)
  const examLevelsHero = examLevels.length > 0 ? examLevels.join(" · ") : "BEPC · Probatoire · BAC"
  const examLevelsProse = examLevels.length > 0 ? joinExamLevelsFr(examLevels) : "le BEPC, le Probatoire et le BAC"

  useSeo({
    // Le titre porte ce que les élèves tapent dans Google ("corrigés BAC Cameroun"),
    // jamais la promesse du produit - personne ne cherche "quoi réviser". C'est la
    // description, affichée sous le titre dans les résultats, qui porte la promesse.
    // "{examens} - {pays}" plutôt que "... au {pays}" : même raison que ci-dessous.
    title: `Corrigés ${examLevels.length > 0 ? examLevels.join(", ") : "BEPC, Probatoire, BAC"}${countryLabel ? ` - ${countryLabel}` : ""}`,
    // "{pays} : ..." plutôt que "... au {pays}" - évite l'accord de genre de la
    // préposition ("au Cameroun" vs "en Côte d'Ivoire") qui varie par pays.
    description: countryLabel
      ? `${countryLabel} : chaque jour, on te dit quoi réviser pour ${examLevelsProse}. Les thèmes qui tombent vraiment, avec corrigés d'annales, cours et quiz.`
      : undefined,
  })

  if (hasLegacyFilters) {
    return <Navigate to={`${epreuvesListPath(country ?? "")}?${searchParams.toString()}`} replace />
  }

  return (
    <div>
      {/* La séance du jour passe AVANT le hero, et seulement pour un élève connecté
          qui a déclaré son cursus (le composant décide seul de s'afficher). Le hero
          reste dessous, intact : /cm est la page la plus indexée du site, elle doit
          rester complète pour un visiteur anonyme comme pour un robot. */}
      <SeanceDuJour country={country ?? ""} />
      {/* Reprise de lecture juste sous la séance du jour : pour qui revient, c'est l'action la
          plus probable de la page - groupée avec sa séance, AVANT la vitrine : tout
          ce qui lui est personnel en haut, l'argumentaire ensuite. Elle vivait tout en
          bas, entre deux rails, après
          cinq écrans de défilement. */}
      {progression && progression.lessons.length > 0 && (
        <div className="mx-auto max-w-5xl px-4 pt-8 sm:px-6">
          <Link
            // getMyProgression() (endpoint access, non modifié par la fusion) ne
            // renvoie jamais que des Lesson classiques - slug toujours renseigné.
            to={epreuveReaderPath(
              progression.lessons[0].subject.country.code.toLowerCase(),
              progression.lessons[0].slug as string,
            )}
            className="group flex animate-fade-up items-center gap-3 rounded-2xl border border-primary/30 bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent px-5 py-4 transition-colors hover:border-primary/50"
          >
            <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <BookOpen className="size-5" />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Reprendre ma lecture
              </span>
              <span className="block truncate font-display font-medium">{progression.lessons[0].title}</span>
            </span>
            <ArrowRight className="size-4 shrink-0 text-primary transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>
      )}
      <section className="relative overflow-hidden border-b border-border">
        <div
          className="absolute inset-0 opacity-[0.05]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "28px 28px",
          }}
        />
        {/* pb-8 et non py-14 : le bandeau de chiffres qui suit appartient au hero, il
            ne doit pas en être séparé par 56 px de vide. */}
        <div className="relative mx-auto grid max-w-5xl gap-8 px-4 pb-8 pt-14 sm:px-6 md:grid-cols-[1.15fr_1fr] md:items-center md:gap-10">
          <div>
            <p className="mb-2 font-display text-sm italic text-primary">
              {examLevelsHero}{countryLabel ? ` - ${countryLabel}` : ""}
            </p>
            {/* La promesse vendait une bibliothèque ("cours structurés et corrigés
                d'annales, classés par matière et par série") alors que le produit est
                devenu un coach : une séance par jour, choisie pour l'élève. Le
                meilleur argument - "tu ne sais pas quoi réviser, on te le dit, et ce
                thème est tombé dans 35 des 41 dernières épreuves" - n'apparaissait
                qu'APRÈS s'être connecté et avoir déclaré son examen, c'est-à-dire
                après la conversion au lieu de la provoquer.

                Le volume reste, mais comme PREUVE et non comme argument : il rassure
                sur le sérieux du corpus, il ne dit pas quoi en faire. */}
            <h1 className="max-w-xl font-display text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
              Chaque jour, on te dit{" "}
              <span className="text-primary">quoi réviser</span>.
            </h1>
            <p className="mt-4 max-w-lg text-muted-foreground">
              Une séance de 25 minutes sur un thème qui tombe vraiment à ton examen : le cours
              pour la méthode, un exercice réellement posé, un quiz pour vérifier. Tu dis ce que
              tu prépares, on s'occupe du reste - et on retient ce que tu rates.
            </p>
            {/* Le premier bouton sert la promesse : sans savoir quel examen l'élève
                prépare, il n'y a pas de séance possible, donc c'est la première chose
                à lui demander - il descend vers la grille des cursus plus bas, qui
                écrit la déclaration. Le second reste ce qu'il y a de gratuit : goûter
                d'abord, payer ensuite (avant, le CTA menait à origine=INEDITE,
                c'est-à-dire au produit le plus cher, pour un visiteur qui n'a encore
                rien lu).

                Pour qui a déjà déclaré son examen, cette question n'a plus lieu
                d'être : sa séance l'attend en haut de page, et ces boutons redeviennent
                ce qu'ils étaient - des portes vers le catalogue. */}
            <div className="mt-6 flex flex-wrap items-center gap-3">
              {aDeclareSonExamen ? (
                <>
                  <Button size="lg" asChild>
                    <Link to={`${epreuvesListPath(country ?? "")}?gratuit=true`}>
                      Lire un corrigé gratuitement
                      <ArrowRight />
                    </Link>
                  </Button>
                  <Button variant="outline" size="lg" asChild>
                    <Link to={epreuvesListPath(country ?? "")}>Chercher une épreuve</Link>
                  </Button>
                </>
              ) : (
                <>
                  <Button size="lg" asChild>
                    <a href="#je-prepare">
                      Dis-nous ce que tu prépares
                      <ArrowRight />
                    </a>
                  </Button>
                  <Button variant="outline" size="lg" asChild>
                    <Link to={`${epreuvesListPath(country ?? "")}?gratuit=true`}>
                      Lire un corrigé gratuitement
                    </Link>
                  </Button>
                </>
              )}
            </div>

            {/* Mention légère plutôt qu'une carte à part entière (voir la discussion
                produit) : l'accueil vient d'être volontairement réduit à trois piliers
                (Épreuves/Cours/Quiz, voir "accueil/catalogue split") et le classement
                n'a pas de sens sans qu'une matière/série soit choisie - ThemesFrequentsPage
                s'en charge, pas cette page. */}
            <Link
              to={themesFrequentsPath(country ?? "")}
              className="mt-3 flex w-fit items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
            >
              <TrendingUp className="size-3.5 text-primary" />
              Découvre les thèmes qui reviennent le plus à ton examen
              <ArrowRight className="size-3" />
            </Link>
          </div>
          <img
            src={heroStudent}
            alt="Élève souriante prenant des notes, ordinateur portable ouvert sur son bureau"
            className="w-full rounded-2xl border border-border"
          />
        </div>

        {/* La page n'affichait aucun chiffre, alors que sa volumétrie est son argument
            le plus crédible - et le seul qu'un concurrent ne peut pas recopier. Tous
            viennent de l'API, aucun n'est écrit en dur.
            Bandeau pleine largeur SOUS la grille à deux colonnes, et non dans sa
            colonne de gauche : là, les trois puces n'avaient que ~550 px et se
            cassaient en 2 + 1, ce qui se lisait comme un accident de mise en page.
            Constaté à l'écran, pas déduit. Ce bandeau comble aussi la couture un peu
            vide entre le hero et la section suivante. */}
        {(epreuvesTotal !== undefined || coursData || subjects.length > 0) && (
          <div className="relative mx-auto flex max-w-5xl flex-wrap gap-2 px-4 pb-14 sm:px-6">
            {epreuvesTotal !== undefined && (
              <StatChip
                icon={<BookOpen className="size-3.5 text-primary" />}
                valeur={formatAmount(epreuvesTotal)}
                libelle={epreuvesTotal > 1 ? "épreuves corrigées" : "épreuve corrigée"}
              />
            )}
            {coursData && (
              <StatChip
                icon={<GraduationCap className="size-3.5 text-gold" />}
                valeur={formatAmount(coursData.count)}
                libelle="cours structurés"
              />
            )}
            {subjects.length > 0 && (
              <StatChip
                icon={<Layers className="size-3.5 text-success" />}
                valeur={String(subjects.length)}
                libelle={subjects.length > 1 ? "matières couvertes" : "matière couverte"}
              />
            )}
          </div>
        )}
      </section>

      {/* La promesse du H1 ("la méthode qui t'apprend à réussir") était affirmée,
          jamais montrée. Extrait réel d'un corrigé publié (voir EXEMPLE_CORRIGE_SLUG),
          rendu par le même composant que la lecture complète (EpreuveMarkdown) - donc
          le même KaTeX, pas une capture d'écran ni un mock. Disparaît silencieusement
          si le slug ne charge pas (même patron que SocialProofSection/EpreuveRail). */}
      {exempleExercice && exempleCorrigeQ1 && (
        <section className="mx-auto max-w-5xl px-4 pt-10 sm:px-6">
          <div className="max-w-2xl">
            <h2 className="font-display text-xl font-semibold">Un exemple, plutôt qu'une promesse</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              {/* exempleContent est forcément défini ici : la section entière est
                  gardée par `exempleExercice && exempleCorrigeQ1`, tous deux dérivés de
                  exempleContent. Le titre ("Mathématiques BEPC 2026") suffit à situer
                  l'examen sans dupliquer matière/niveau/année séparément. */}
              Extrait réel d'un corrigé de {exempleContent?.title} - la méthode expliquée à chaque étape, pas
              seulement le résultat final.
            </p>
          </div>
          <div className="mt-5 rounded-2xl border border-border bg-card p-5 sm:p-8">
            {/* enonce_intro_markdown ("**Exercice 1 (2 points)**") situe l'extrait comme
                un vrai exercice noté, pas une phrase retouchée pour la démonstration. */}
            {exempleExercice.enonce_intro_markdown && (
              <div className="mb-4 text-sm font-semibold text-primary">
                <EpreuveMarkdown markdown={exempleExercice.enonce_intro_markdown} />
              </div>
            )}
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-primary">Corrigé pas à pas</p>
            {/* Corrigé complet de la question 1 (voir exempleCorrigeQ1), jamais tronqué :
                il commence déjà par l'énoncé de la question 1 lui-même, donc pas de
                section "Énoncé" séparée qui le répéterait. */}
            <div className="prose prose-neutral max-w-none text-sm dark:prose-invert prose-headings:font-display">
              <EpreuveMarkdown markdown={exempleCorrigeQ1} />
            </div>
            <div className="mt-4 flex justify-center border-t border-border pt-4">
              <Button asChild variant="outline">
                <Link to={epreuveReaderPath(country ?? "", EXEMPLE_CORRIGE_SLUG)}>
                  Lire le corrigé complet
                  <ArrowRight />
                </Link>
              </Button>
            </div>
          </div>
        </section>
      )}


      {/* La question qui qualifie tout le reste, posée en premier. Elle était repliée
          dans "Filtres avancés" : un élève de Terminale D devait ouvrir un panneau et
          lire une liste de 11 cursus pour dire ce qu'il prépare.

          Masquée pour qui a DÉJÀ déclaré son examen : sa séance du jour affiche son
          cursus et son compte à rebours en haut de cette même page, et on lui
          redemandait "Qu'est-ce que tu prépares ?" quelques centaines de pixels plus
          bas. La même phrase pour deux choses différentes - déclarer d'un côté,
          filtrer le catalogue de l'autre. Pour lui, l'entrée "Réviser" du menu mène au
          même catalogue avec ses filtres. */}
      {cursusList.length > 0 && !aDeclareSonExamen && (
        <section id="je-prepare" className="mx-auto max-w-5xl scroll-mt-24 px-4 pt-10 sm:px-6">
          <h2 className="font-display text-xl font-semibold">Qu'est-ce que tu prépares ?</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Choisis ton examen et ta série : le catalogue se filtre pour toi.
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            {examCodesFor(cursusList).map((examen) => {
              const duNiveau = cursusList.filter((c) => c.examen === examen.code)
              return (
                <div key={examen.code} className="rounded-xl border border-border bg-card p-4">
                  <p className="font-display font-semibold">{examen.label}</p>
                  <div className="mt-2.5 flex flex-wrap gap-1.5">
                    {duNiveau.map((c) => (
                      <Link
                        key={c.id}
                        to={`${epreuvesListPath(country ?? "")}?cursus=${c.id}`}
                        className={cn(
                          "rounded-full border border-border px-3 py-1.5 text-center text-xs font-medium text-muted-foreground transition-colors hover:border-primary/40 hover:text-primary",
                          // Un examen sans série (le BEPC) n'a qu'une seule pastille :
                          // à côté des six du Probatoire, sa carte se lisait à moitié
                          // vide. En pleine largeur elle occupe sa carte comme les
                          // autres. Constaté à l'écran.
                          !c.series && "w-full",
                        )}
                      >
                        {/* Réafficher le nom de l'examen ne dirait rien de plus que le
                            titre juste au-dessus. */}
                        {c.series ? `Série ${c.series.code}` : "Voir les épreuves"}
                      </Link>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        </section>
      )}

      {/* Les portes d'entrée du produit. Rien sur cette page ne disait qu'elles
          existent : il fallait les déduire du menu du header. Grille à exactement
          quatre cartes (jamais un nombre impair qui laisserait une orpheline sur sa
          propre ligne, constaté à l'écran) - "Épreuves Inédites" en sort volontairement
          pour un bandeau pleine largeur ci-dessous plutôt que de rejoindre la grille :
          le produit le plus cher de la maison mérite de se distinguer, pas de se fondre
          dans le même gabarit que les trois portes d'entrée gratuites. Jusqu'ici son
          unique présence sur cette page était l'encart vedette plus bas, entièrement
          masqué quand aucune inédite récente n'a d'aperçu public (voir inediteVedette).
          Ce bandeau ne dépend que de inediteRecenteData.count : il reste visible même
          quand l'encart vedette ne l'est pas. */}
      <section className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        {/* Le récit du plan, à la place d'une grille de quatre portes (Épreuves,
            Cours, Parcours, Quiz). Cette grille décrivait notre modèle de données -
            deux types de documents et deux outils - et laissait l'élève composer son
            itinéraire lui-même, exactement ce dont la séance du jour le décharge. Elle
            contredisait aussi la navigation, réduite depuis à trois entrées.
            Les quatre destinations restent atteignables : "Réviser" dans le menu, et
            le bandeau Épreuves Inédites juste en dessous pour le produit payant. */}
        <h2 className="font-display text-xl font-semibold">Comment ça marche</h2>
        <div className="mt-4 grid gap-5 sm:grid-cols-3">
          <EtapeExplication
            numero="1"
            titre="Tu dis ce que tu prépares"
            description="Ton examen et ta série, une fois. Le compte à rebours jusqu'au jour J démarre, et tout ce que tu vois ensuite ne concerne plus que toi."
          />
          <EtapeExplication
            numero="2"
            titre="On te donne une séance par jour"
            description="Un thème qui tombe vraiment - on te dit dans combien des dernières épreuves. Le cours pour la méthode, un exercice réellement posé, un quiz pour vérifier. 25 minutes."
          />
          <EtapeExplication
            numero="3"
            titre="On retient ce que tu rates"
            description="Un thème raté revient demain, puis dans trois jours, puis dans une semaine - jusqu'à ce qu'il soit acquis. Tu n'as rien à noter, rien à planifier."
          />
        </div>
        {inediteRecenteData && inediteRecenteData.count > 0 && (
          <Link
            to={`${epreuvesListPath(country ?? "")}?${requeteInedites(cursusAccueil)}`}
            className="group mt-5 flex flex-col items-start gap-4 rounded-2xl border border-gold/40 bg-gradient-to-b from-gold/5 to-card p-5 transition-all duration-300 hover:-translate-y-1 hover:border-gold/60 hover:shadow-lg hover:shadow-gold/10 sm:flex-row sm:items-center sm:gap-5 sm:p-6"
          >
            <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold">
              <Crown className="size-5" />
            </span>
            <div className="flex-1">
              <h3 className="flex flex-wrap items-center gap-2 font-display text-lg font-semibold">
                Épreuves Inédites
                <span className="rounded-full bg-gold/15 px-2.5 py-0.5 text-[10px] font-bold tracking-wide text-gold uppercase">
                  Exclusif
                </span>
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Un sujet original conçu par Edukora, jamais tiré des annales - même niveau, même barème que l'épreuve réelle, dans les conditions du jour J.
              </p>
            </div>
            <span className="flex shrink-0 items-center gap-1.5 text-sm font-medium text-gold">
              Explorer
              <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
            </span>
          </Link>
        )}
      </section>

      {/* Différenciation face aux annales/corrigés déjà gratuits sur Internet (audit UX
          externe, 2026-09-04) - la grille "Comment travailler" ci-dessus dit CE QUE le
          produit contient, jamais POURQUOI ça vaut mieux qu'un PDF trouvé ailleurs. Les
          quatre points reprennent des mécanismes déjà montrés plus haut sur cette même
          page (quiz, corrigés pas à pas, thèmes fréquents, inédites) plutôt que des
          promesses nouvelles - jamais un argument que le reste de la page ne prouve pas. */}
      <section className="mx-auto max-w-5xl px-4 pb-10 sm:px-6">
        <h2 className="font-display text-xl font-semibold">Pourquoi Edukora ?</h2>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
          Les annales et leurs corrigés existent déjà gratuitement sur Internet. Voici ce qu'Edukora fait en plus.
        </p>
        <div className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-border bg-card p-5">
            <span className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <Target className="size-5" />
            </span>
            <h3 className="mt-3 font-display text-base font-semibold">Tu sais quoi réviser</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Le quiz repère tes lacunes et te fait réviser exactement ce qu'il faut, au bon moment.
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-card p-5">
            <span className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <GraduationCap className="size-5" />
            </span>
            <h3 className="mt-3 font-display text-base font-semibold">Tu comprends, pas seulement tu mémorises</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Des cours structurés et des corrigés expliqués étape par étape, pas juste le résultat final.
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-card p-5">
            <span className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <TrendingUp className="size-5" />
            </span>
            <h3 className="mt-3 font-display text-base font-semibold">Tu vises ce qui tombe vraiment</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Le classement des thèmes les plus posés à ton examen, calculé sur les vraies annales.
            </p>
          </div>
          <div className="rounded-2xl border border-gold/30 bg-gold/5 p-5">
            <span className="flex size-10 items-center justify-center rounded-xl bg-gold/15 text-gold">
              <Crown className="size-5" />
            </span>
            <h3 className="mt-3 font-display text-base font-semibold">Tu te testes sur l'inconnu</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Des épreuves inédites, jamais tirées des annales, pour vérifier que tu maîtrises vraiment le programme.
            </p>
          </div>
        </div>
      </section>

      {/* Pendant du "Un exemple, plutôt qu'une promesse" plus haut, mais pour Inédites -
          jamais un rail de cartes (qui la ferait ressembler à une liste de plus parmi
          tant d'autres sur cette page) : une vraie question de l'épreuve la plus
          récente, gratuite et publique (apercu_enonce_markdown), sous le même principe
          que le hero n'a jamais appliqué à ce produit. Positionnée après les portes
          d'entrée plutôt que dans le hero : le CTA du hero reste dédié au contenu
          gratuit (voir plus haut) pour un visiteur qui n'a encore rien lu - celui qui
          arrive jusqu'ici a déjà vu de quoi il retourne. Si aucune inédite récente n'a
          d'aperçu public, repli compact juste en dessous plutôt que silence complet -
          la carte "Épreuves Inédites" de la grille au-dessus reste de toute façon
          visible dans les deux cas. */}
      {inediteVedette?.apercu_enonce_markdown && (
        <section className="mx-auto max-w-5xl px-4 pt-4 sm:px-6 mb-8">
          <div className="rounded-2xl border border-gold/30 bg-gold/5 p-5 sm:p-8">
            <div className="flex flex-wrap items-center gap-2">
              <span className="flex items-center gap-1.5 rounded-full bg-gold/15 px-3 py-1 text-xs font-semibold text-gold">
                <Crown className="size-3.5" />
                Épreuve inédite
              </span>
              {inediteVedette.duree_minutes && (
                <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Clock className="size-3.5" />
                  Chronométrée - {inediteVedette.duree_minutes} min
                </span>
              )}
            </div>
            <h2 className="mt-3 font-display text-xl font-semibold">{inediteVedette.title}</h2>
            <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
              Une épreuve originale conçue par Edukora, jamais tirée des annales - même niveau, même barème que
              l'examen réel. Voici la première question, en accès libre.
            </p>
            <div className="mt-5 rounded-xl border border-border bg-card p-5 sm:p-6">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gold">Aperçu</p>
              <div className="prose prose-neutral max-w-none text-sm dark:prose-invert prose-headings:font-display">
                <EpreuveMarkdown markdown={inediteVedette.apercu_enonce_markdown} />
              </div>
            </div>
            <div className="mt-4 flex flex-wrap justify-center gap-3">
              <Button asChild>
                <Link to={epreuveInediteDetailPath(country ?? "", inediteVedette.slug ?? inediteVedette.id)}>
                  Découvrir cette épreuve
                  <ArrowRight />
                </Link>
              </Button>
              {/* La vedette n'est qu'une parmi d'autres (voir inediteRecenteData.count) -
                  sans ce second lien, un visiteur convaincu par l'aperçu n'avait aucun
                  moyen de savoir que d'autres inédites existent pour d'autres matières. */}
              <Button asChild variant="outline">
                <Link to={`${epreuvesListPath(country ?? "")}?${requeteInedites(cursusAccueil)}`}>
                  {inediteRecenteData && inediteRecenteData.count > 1
                    ? `Voir les ${inediteRecenteData.count} épreuves inédites`
                    : "Voir toutes les épreuves inédites"}
                </Link>
              </Button>
            </div>
          </div>
        </section>
      )}

      {/* Repli du bloc ci-dessus : il existe des inédites pour ce pays, mais aucune
          n'a d'aperçu public à montrer. `inediteVedetteLoading` évite un flash de ce
          bandeau avant que l'encart complet ne le remplace le cas échéant. Pas de
          question ni de matière précise ici (rien de fiable à afficher) - juste un
          rappel de l'offre et un lien vers la liste, plutôt que de faire disparaître
          la section entière comme aujourd'hui. */}
      {!inediteVedette?.apercu_enonce_markdown &&
        !inediteVedetteLoading &&
        inediteRecenteData &&
        inediteRecenteData.count > 0 && (
          <section className="mx-auto max-w-5xl px-4 pt-4 sm:px-6 mb-8">
            <div className="flex flex-wrap items-center gap-4 rounded-2xl border border-gold/30 bg-gold/5 p-5 sm:p-6">
              <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold">
                <Crown className="size-5" />
              </span>
              <div className="flex-1">
                <h2 className="font-display text-base font-semibold">Des épreuves inédites t'attendent</h2>
                <p className="mt-0.5 text-sm text-muted-foreground">
                  Des sujets originaux conçus par Edukora, dans les conditions du jour J.
                </p>
              </div>
              <Button asChild>
                <Link to={`${epreuvesListPath(country ?? "")}?${requeteInedites(cursusAccueil)}`}>
                  Voir les épreuves inédites
                  <ArrowRight />
                </Link>
              </Button>
            </div>
          </section>
        )}

      {/* Dernière section de la page : la preuve sociale construit la confiance du
          visiteur qui vient de voir ce qu'il y a à lire (la section "Un exemple,
          plutôt qu'une promesse" plus haut), avant qu'il ne reparte chercher lui-même
          dans le catalogue ou les tarifs. L'accueil ne porte plus aucun rail de
          cartes générique : "À lire gratuitement" a été retiré - la section exemple
          plus haut en tient déjà lieu, et le CTA du hero mène à du contenu gratuit réel
          en un clic (voir /epreuves?gratuit=true). Le catalogue complet, lui, vit sur sa
          propre URL (voir EpreuvesListPage) plutôt qu'en bas de celle-ci. */}
      <SocialProofSection />

      {/* Dernière section avant le footer (audit UX externe, 2026-09-04) : la page
          démontrait la valeur du produit (démo de corrigé, inédites, preuve sociale)
          sans jamais pousser explicitement vers l'abonnement - un visiteur convaincu
          n'avait que le menu du header pour trouver /tarifs. Pas de prix ici : ils
          dépendent du cursus (voir PricingPage/Plan.effective_price), les répéter en
          dur ici les désynchroniserait silencieusement de la vraie grille. */}
      <section className="mx-auto max-w-5xl px-4 pb-14 sm:px-6">
        <div className="relative overflow-hidden rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent p-6 text-center sm:p-10">
          <div
            className="absolute inset-0 opacity-[0.04]"
            style={{
              backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
              backgroundSize: "24px 24px",
            }}
          />
          <div className="relative">
            <h2 className="font-display text-2xl font-semibold">Prêt à commencer ?</h2>
            <p className="mx-auto mt-2 max-w-xl text-muted-foreground">
              Un seul abonnement, valable jusqu'à ton examen, moins cher chaque mois qui passe. Paiement par Mobile
              Money, sans engagement.
            </p>
            <div className="mt-5 flex justify-center">
              <Button size="lg" asChild>
                <Link to="/tarifs">
                  Voir les tarifs
                  <ArrowRight />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}


/**
 * Trois publics, trois pages - c'est le même /cm pour tous les trois.
 *
 *   - visiteur anonyme       -> la vitrine, inchangée (et c'est ce que voient les
 *                               robots, qui n'ont jamais de session : le contenu
 *                               indexé de la page la plus référencée du site ne
 *                               bouge pas) ;
 *   - élève SANS abonnement  -> la vitrine aussi, avec sa séance verrouillée en
 *                               tête : c'est sa page de conversion ;
 *   - élève ABONNÉ           -> ses affaires, et rien d'autre.
 *
 * Le branchement vit ici, dans un composant qui n'appelle qu'un seul hook, et pas
 * dans un `return` anticipé au milieu de la vitrine : les quinze requêtes du
 * catalogue ne partent ainsi jamais pour un élève qui ne verra pas cette page.
 *
 * Pendant que l'authentification se résout (un aller-retour de rafraîchissement au
 * démarrage), c'est la vitrine qui s'affiche. C'est volontaire : c'est le seul défaut
 * sûr pour un robot ou un visiteur, qui sont la majorité des arrivées sur cette URL.
 * Un élève abonné voit donc brièvement la vitrine avant sa page - à corriger avec un
 * indice mémorisé côté navigateur si la bascule se voit trop.
 */
export function CataloguePage() {
  const { isAuthenticated, user } = useAuth()
  const { country } = useParams<{ country: string }>()

  if (isAuthenticated && user?.cursus_prepare && user.a_un_abonnement_actif) {
    return <AccueilEleve country={country ?? ""} />
  }
  return <CatalogueVitrine />
}
