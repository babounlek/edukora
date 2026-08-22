import { useEffect, type ReactNode } from "react"
import { Link, Navigate, useParams, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, BookOpen, Clock, Crown, GraduationCap, Layers, Target } from "lucide-react"

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
import { coursListPath, epreuveInediteDetailPath, epreuveReaderPath, epreuvesListPath } from "@/lib/countryPath"
import { cn, formatAmount } from "@/lib/utils"
import { EpreuveMarkdown } from "@/components/EpreuveMarkdown"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Button } from "@/components/ui/button"
import { SocialProofSection } from "@/components/SocialProofSection"

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

interface UniversProps {
  icon: ReactNode
  titre: string
  chiffre: string | null
  description: string
  to: string
  /** Seule "Épreuves Inédites" l'utilise : le produit le plus cher de la maison
   * mérite de se distinguer visuellement des trois portes d'entrée gratuites,
   * plutôt que de se fondre dans la même grille. */
  dore?: boolean
}

/** Une des portes d'entrée du produit. La page d'accueil n'expliquait nulle part
 * qu'elles existent : elle listait des épreuves et laissait deviner le reste depuis
 * le menu du header. */
function CarteUnivers({ icon, titre, chiffre, description, to, dore = false }: UniversProps) {
  return (
    <Link
      to={to}
      className={cn(
        "group relative flex flex-col gap-2 rounded-2xl border p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-lg",
        dore
          ? "border-gold/40 bg-gradient-to-b from-gold/5 to-card hover:border-gold/60 hover:shadow-gold/10"
          : "border-border bg-card hover:border-primary/50 hover:shadow-primary/5",
      )}
    >
      {dore && (
        <span className="absolute top-5 right-5 rounded-full bg-gold/15 px-2.5 py-0.5 text-[10px] font-bold tracking-wide text-gold uppercase">
          Exclusif
        </span>
      )}
      <span
        className={cn(
          "flex size-10 items-center justify-center rounded-xl",
          dore ? "bg-gold/15 text-gold" : "bg-primary/10 text-primary",
        )}
      >
        {icon}
      </span>
      <h3 className="font-display text-lg font-semibold">
        {titre}
        {chiffre && <span className="ml-2 text-sm font-normal tabular-nums text-muted-foreground">{chiffre}</span>}
      </h3>
      <p className="flex-1 text-sm text-muted-foreground">{description}</p>
      <span className={cn("flex items-center gap-1.5 text-sm font-medium", dore ? "text-gold" : "text-primary")}>
        Explorer
        <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-0.5" />
      </span>
    </Link>
  )
}

export function CataloguePage() {
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = countries.find((c) => c.code.toLowerCase() === country)?.label
  const { isAuthenticated } = useAuth()
  const [searchParams] = useSearchParams()

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
  const { data: inediteRecenteData } = useQuery({
    queryKey: ["epreuves-inedites-recente", country],
    queryFn: ({ signal }) => listEpreuves({ country, origine: "INEDITE", ordering: "recent" }, signal),
    enabled: Boolean(country) && !hasLegacyFilters,
  })
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
    title: "Cours, corrigés et quiz - BEPC, Probatoire, BAC",
    // "{pays} : ..." plutôt que "... au {pays}" - évite l'accord de genre de la
    // préposition ("au Cameroun" vs "en Côte d'Ivoire") qui varie par pays.
    description: countryLabel
      ? `${countryLabel} : cours structurés, corrigés d'annales et quiz d'entraînement pour ${examLevelsProse}, classés par matière et par série.`
      : undefined,
  })

  if (hasLegacyFilters) {
    return <Navigate to={`${epreuvesListPath(country ?? "")}?${searchParams.toString()}`} replace />
  }

  return (
    <div>
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
            <h1 className="max-w-xl font-display text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
              La méthode qui t'apprend{" "}
              <span className="text-primary">à réussir</span>, pas juste la réponse.
            </h1>
            <p className="mt-4 max-w-lg text-muted-foreground">
              Cours structurés et corrigés d'annales, classés par matière et par série - avec
              un quiz qui repère tes lacunes et te fait réviser exactement ce qu'il faut, au
              bon moment.
            </p>
            {/* Le CTA menait à origine=INEDITE, c'est-à-dire au produit le plus cher
                de la maison, pour un visiteur qui n'a encore rien lu. Il mène
                maintenant à ce qu'il y a de gratuit : goûter d'abord, payer ensuite.
                Le second lien mène au moteur de recherche du catalogue, pour qui sait
                déjà ce qu'il cherche. */}
            <div className="mt-6 flex flex-wrap items-center gap-3">
              <Button size="lg" asChild>
                <Link to={`${epreuvesListPath(country ?? "")}?gratuit=true`}>
                  Lire un corrigé gratuitement
                  <ArrowRight />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link to={epreuvesListPath(country ?? "")}>Chercher une épreuve</Link>
              </Button>
            </div>

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

      {/* Reprise de lecture juste sous le hero : pour qui revient, c'est l'action la
          plus probable de la page. Elle vivait tout en bas, entre deux rails, après
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

      {/* La question qui qualifie tout le reste, posée en premier. Elle était repliée
          dans "Filtres avancés" : un élève de Terminale D devait ouvrir un panneau et
          lire une liste de 11 cursus pour dire ce qu'il prépare. */}
      {cursusList.length > 0 && (
        <section className="mx-auto max-w-5xl px-4 pt-10 sm:px-6">
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
          existent : il fallait les déduire du menu du header. "Épreuves Inédites"
          rejoint la grille (voir dore=true sur CarteUnivers) - jusqu'ici son unique
          présence sur cette page était l'encart vedette plus bas, entièrement masqué
          quand aucune inédite récente n'a d'aperçu public (voir inediteVedette). Cette
          carte-ci ne dépend que de inediteRecenteData.count : elle reste visible même
          quand l'encart vedette ne l'est pas. */}
      <section className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        <h2 className="font-display text-xl font-semibold">Comment travailler sur Edukora</h2>
        <div className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <CarteUnivers
            icon={<BookOpen className="size-5" />}
            titre="Épreuves"
            chiffre={epreuvesTotal !== undefined ? formatAmount(epreuvesTotal) : null}
            description="Annales, examens blancs et épreuves d'établissement, corrigés pas à pas plutôt que résolus en trois lignes."
            to={epreuvesListPath(country ?? "")}
          />
          <CarteUnivers
            icon={<GraduationCap className="size-5" />}
            titre="Cours"
            chiffre={coursData ? formatAmount(coursData.count) : null}
            description="Chaque notion du programme : la règle, un exemple résolu, les erreurs classiques et des exercices gradués."
            to={coursListPath(country ?? "")}
          />
          <CarteUnivers
            icon={<Target className="size-5" />}
            titre="Quiz"
            chiffre={null}
            description="Il repère les thèmes où tu échoues et te les repropose au bon moment, jusqu'à ce qu'ils soient acquis."
            to="/quiz"
          />
          {inediteRecenteData && inediteRecenteData.count > 0 && (
            <CarteUnivers
              dore
              icon={<Crown className="size-5" />}
              titre="Épreuves Inédites"
              chiffre={null}
              description="Un sujet d'examen jamais vu, jamais publié ailleurs - même niveau, même barème que l'épreuve réelle, dans les conditions du jour J."
              to={`${epreuvesListPath(country ?? "")}?origine=INEDITE`}
            />
          )}
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
              Une épreuve d'examen jamais vue, jamais publiée ailleurs - même niveau, même barème que l'examen réel.
              Voici la première question, en accès libre.
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
                <Link to={`${epreuvesListPath(country ?? "")}?origine=INEDITE`}>
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
                  Des sujets jamais publiés ailleurs, dans les conditions du jour J.
                </p>
              </div>
              <Button asChild>
                <Link to={`${epreuvesListPath(country ?? "")}?origine=INEDITE`}>
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
    </div>
  )
}
