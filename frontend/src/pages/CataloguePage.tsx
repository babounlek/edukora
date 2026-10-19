import { useEffect, type ReactNode } from "react"
import { Link, Navigate, useParams, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, BookOpen, Clock, Crown, GraduationCap, Layers, Target, TrendingUp } from "lucide-react"

import heroStudent from "@/assets/hero-student.jpg"
import {
  getEpreuveInedite,
  getMyProgression,
  listSubjects,
  readEpreuve,
} from "@/api/endpoints"
import { trackEvent } from "@/lib/analytics"
import { nomPays } from "@/lib/pays"
import { examLevelsFor, joinExamLevelsProse } from "@/lib/cursus"
import { langueDeListe } from "@/lib/discipline"
import { langueCourante, t, tn, useI18n } from "@/lib/i18n"
import { useCursusListe } from "@/lib/cursusLangue"
import { exempleDuCursus, extraireExempleCorrige } from "@/lib/exempleCorrige"
import { libelleEnteteExercice } from "@/lib/libellesEpreuve"
import { useTotalCours, useTotalEpreuves } from "@/lib/totauxCatalogue"
import { PRIX_ABONNEMENT_FCFA, PRIX_ENFANT_SUPPLEMENTAIRE_FCFA } from "@/lib/tarifs"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import {
  epreuveInediteDetailPath,
  epreuveReaderPath,
  epreuvesListPath,
  themesFrequentsPath,
} from "@/lib/countryPath"
import { formatAmount } from "@/lib/utils"
import { EpreuveMarkdownLazy } from "@/components/EpreuveMarkdownLazy"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Button } from "@/components/ui/button"
import { SocialProofSection } from "@/components/SocialProofSection"
import { SeanceDuJour } from "@/components/SeanceDuJour"
import { AccueilEleve } from "@/components/AccueilEleve"
import { InviteAutreSousSystemeDuPays } from "@/components/InviteAutreSousSysteme"
import { requeteInedites, useCursusAccueil, useInedites } from "@/lib/cursusAccueil"

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
  // S'abonne au changement de langue : les `t(...)` ci-dessous se relisent à chaque bascule.
  useI18n()
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = nomPays(countries, country)
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
    // Le catalogue d'accueil montre les matières de la langue de l'interface (voir lib/discipline.langueDeListe).
    queryKey: ["subjects", country, langueDeListe("", false)],
    queryFn: ({ signal }) => listSubjects(country, signal, undefined, langueDeListe("", false)),
  })

  // Les examens annoncés suivent la langue de l'interface (voir lib/cursusLangue) : « BEPC · Probatoire · BAC »
  // en français, « GCE O Level · GCE A Level » en anglais.
  const { data: cursusList } = useCursusListe(country, { langue: langueDeListe("", false) })

  // Extrait réel d'un corrigé, pour la section "preuve" du hero (voir plus bas) - la
  // promesse du H1 ("la méthode qui t'apprend à réussir") doit se montrer, pas
  // seulement s'affirmer. `retry: false` : un 404 (slug renommé/retiré) doit faire
  // disparaître la section silencieusement, pas insister avec des tentatives inutiles.
  // L'épreuve d'exemple suit la langue de l'interface (voir lib/exempleCorrige) : un BEPC en français,
  // un GCE en anglais - et l'examen déclaré quand une mathématique gratuite existe pour lui (BAC C, D, E).
  // Le slug fait partie de la clé de cache, donc un changement de langue ou d'examen recharge.
  const cursusAccueil = useCursusAccueil(country ?? "")
  const exemple = exempleDuCursus(langueCourante(), cursusList?.find((c) => c.id === cursusAccueil))
  const { data: exempleContent } = useQuery({
    queryKey: ["epreuve-exemple-corrige", exemple.slug],
    queryFn: () => readEpreuve(exemple.slug),
    enabled: !hasLegacyFilters,
    retry: false,
  })
  // Le corrigé à montrer (question 1 seule ou exercice entier, selon l'exemple) : voir extraireExempleCorrige.
  const extrait = extraireExempleCorrige(exempleContent, exemple)
  const exempleExercice = extrait?.exercice
  const exempleCorrigeQ1 = extrait?.corrigeMarkdown

  // Volume de cours du pays, pour la puce du hero et la carte "Cours" - même clé de
  // cache que /cours (voir CoursListPage), donc un aller-retour entre les deux pages
  // ne repaie pas la requête.
  // Dans la langue de l'interface, comme les matières et les épreuves : la puce annonce ce que /cours affichera.
  const langueAccueil = langueDeListe("", false)
  const { data: coursData } = useTotalCours(country, langueAccueil, !hasLegacyFilters)

  // Volumétrie totale d'épreuves annoncée par le hero - même clé de cache que sur
  // /epreuves (voir EpreuvesListPage), donc un aller-retour entre les deux pages ne
  // repaie pas la requête.
  const { data: epreuvesTotalData } = useTotalEpreuves(country, langueAccueil, !hasLegacyFilters)
  const epreuvesTotal = epreuvesTotalData?.count

  // Épreuve inédite mise en avant, pour la section "preuve" dédiée plus bas - jamais un
  // slug codé en dur (contrairement à EXEMPLES_CORRIGE) : la plus récente pour ce
  // pays, redécouverte à chaque chargement, donc jamais périmée si le contenu change.
  // Restreinte au cursus déclaré (compte ou onboarding) quand il y en a un : voir
  // useInedites.
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
  const examLevelsHero = examLevels.length > 0 ? examLevels.join(" · ") : langueDeListe("", false) === "en" ? "GCE O Level · GCE A Level" : "BEPC · Probatoire · BAC"
  const examLevelsProse = examLevels.length > 0 ? joinExamLevelsProse(examLevels) : t("accueil.examens_repli")

  useSeo({
    // Le titre porte ce que les élèves tapent dans Google ("corrigés BAC Cameroun"),
    // jamais la promesse du produit - personne ne cherche "quoi réviser". C'est la
    // description, affichée sous le titre dans les résultats, qui porte la promesse.
    // "{examens} - {pays}" plutôt que "... au {pays}" : même raison que ci-dessous.
    title: countryLabel
      ? t("accueil.seo_titre_pays", { examens: examLevels.length > 0 ? examLevels.join(", ") : "BEPC, Probatoire, BAC", pays: countryLabel })
      : t("accueil.seo_titre", { examens: examLevels.length > 0 ? examLevels.join(", ") : "BEPC, Probatoire, BAC" }),
    // "{pays} : ..." plutôt que "... au {pays}" - évite l'accord de genre de la
    // préposition ("au Cameroun" vs "en Côte d'Ivoire") qui varie par pays.
    description: countryLabel
      ? t("accueil.seo_description", { pays: countryLabel, examens: examLevelsProse })
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
                {t("accueil.reprendre_lecture")}
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
              {t("accueil.hero_titre_debut")}{" "}
              <span className="text-primary">{t("accueil.hero_titre_accent")}</span>.
            </h1>
            <p className="mt-4 max-w-lg text-muted-foreground">
              {t("accueil.hero_texte")}
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
              <Button size="lg" asChild>
                <Link to={`${epreuvesListPath(country ?? "")}?gratuit=true`}>
                  {t("accueil.cta_corrige_gratuit")}
                  <ArrowRight />
                </Link>
              </Button>
              {/* Le quiz gratuit est la façon la plus rapide de goûter au produit (une minute, un
                  résultat) et il ne demande pas de compte. La recherche d'épreuve n'a plus de bouton
                  ici : « Épreuves » et la loupe de l'en-tête la portent sur toutes les pages. Pour un
                  visiteur connecté, « sans compte » serait faux. */}
              <Button variant="outline" size="lg" asChild className="border-primary/40 text-primary hover:text-primary">
                <Link to="/quiz">
                  <Target />
                  {isAuthenticated ? t("accueil.cta_quiz_connecte") : t("accueil.cta_quiz_anonyme")}
                </Link>
              </Button>
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
              {t("accueil.themes_frequents")}
              <ArrowRight className="size-3" />
            </Link>
            {/* Pour qui prépare l'autre sous-système (le GCE sur la version française, le BAC sur
                l'anglaise) : la page ne propose que les examens de sa langue. */}
            <InviteAutreSousSystemeDuPays className="mt-3" />
          </div>
          <img
            src={heroStudent}
            alt={t("accueil.hero_alt")}
            // Image du premier écran (probablement l'élément le plus grand = LCP) : priorité de
            // téléchargement, et dimensions réservées pour que le texte ne saute pas à son arrivée.
            fetchPriority="high"
            width={816}
            height={499}
            className="h-auto w-full rounded-2xl border border-border"
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
                libelle={tn("accueil.stat_epreuves", epreuvesTotal > 1 ? 2 : 1)}
              />
            )}
            {coursData && (
              <StatChip
                icon={<GraduationCap className="size-3.5 text-gold-text" />}
                valeur={formatAmount(coursData.count)}
                libelle={t("accueil.stat_cours")}
              />
            )}
            {subjects.length > 0 && (
              <StatChip
                icon={<Layers className="size-3.5 text-success" />}
                valeur={String(subjects.length)}
                libelle={tn("accueil.stat_matieres", subjects.length > 1 ? 2 : 1)}
              />
            )}
          </div>
        )}
      </section>

      {/* La promesse du H1 ("la méthode qui t'apprend à réussir") était affirmée,
          jamais montrée. Extrait réel d'un corrigé publié (voir EXEMPLES_CORRIGE),
          rendu par le même composant que la lecture complète (EpreuveMarkdown) - donc
          le même KaTeX, pas une capture d'écran ni un mock. Disparaît silencieusement
          si le slug ne charge pas (même patron que SocialProofSection/EpreuveRail). */}
      {exempleExercice && exempleCorrigeQ1 && (
        <section className="mx-auto max-w-5xl px-4 pt-10 sm:px-6">
          <div className="max-w-2xl">
            <h2 className="font-display text-xl font-semibold">{t("accueil.exemple_titre")}</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              {/* exempleContent est forcément défini ici : la section entière est
                  gardée par `exempleExercice && exempleCorrigeQ1`, tous deux dérivés de
                  exempleContent. Le titre ("Mathématiques BEPC 2026") suffit à situer
                  l'examen sans dupliquer matière/niveau/année séparément. */}
              {t("accueil.exemple_texte", { titre: exempleContent?.title ?? "" })}
            </p>
          </div>
          <div className="mt-5 rounded-2xl border border-border bg-card p-5 sm:p-8">
            {/* enonce_intro_markdown ("**Exercice 1 (2 points)**") situe l'extrait comme
                un vrai exercice noté, pas une phrase retouchée pour la démonstration. */}
            {exempleExercice.enonce_intro_markdown && (
              <div className="mb-4 text-sm font-semibold text-primary">
                <EpreuveMarkdownLazy markdown={libelleEnteteExercice(exempleExercice.enonce_intro_markdown)} />
              </div>
            )}
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-primary">{t("accueil.corrige_pas_a_pas")}</p>
            {/* Corrigé complet de la question 1 (voir exempleCorrigeQ1), jamais tronqué :
                il commence déjà par l'énoncé de la question 1 lui-même, donc pas de
                section "Énoncé" séparée qui le répéterait. */}
            <div className="prose prose-neutral max-w-none text-sm dark:prose-invert prose-headings:font-display">
              <EpreuveMarkdownLazy markdown={exempleCorrigeQ1} />
            </div>
            <div className="mt-4 flex justify-center border-t border-border pt-4">
              <Button asChild variant="outline">
                <Link to={epreuveReaderPath(country ?? "", exemple.slug)}>
                  {t("accueil.lire_corrige_complet")}
                  <ArrowRight />
                </Link>
              </Button>
            </div>
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
        <h2 className="font-display text-xl font-semibold">{t("accueil.comment_titre")}</h2>
        <div className="mt-4 grid gap-5 sm:grid-cols-3">
          <EtapeExplication
            numero="1"
            titre={t("accueil.etape1_titre")}
            description={t("accueil.etape1_texte")}
          />
          <EtapeExplication
            numero="2"
            titre={t("accueil.etape2_titre")}
            description={t("accueil.etape2_texte")}
          />
          <EtapeExplication
            numero="3"
            titre={t("accueil.etape3_titre")}
            description={t("accueil.etape3_texte")}
          />
        </div>
        {inediteRecenteData && inediteRecenteData.count > 0 && (
          <Link
            to={`${epreuvesListPath(country ?? "")}?${requeteInedites(cursusAccueil)}`}
            className="group mt-5 flex flex-col items-start gap-4 rounded-2xl border border-gold/40 bg-gradient-to-b from-gold/5 to-card p-5 transition-all duration-300 hover:-translate-y-1 hover:border-gold/60 hover:shadow-lg hover:shadow-gold/10 sm:flex-row sm:items-center sm:gap-5 sm:p-6"
          >
            <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
              <Crown className="size-5" />
            </span>
            <div className="flex-1">
              <h3 className="flex flex-wrap items-center gap-2 font-display text-lg font-semibold">
                {t("accueil.inedites_titre")}
                <span className="rounded-full bg-gold/15 px-2.5 py-0.5 text-xs font-bold tracking-wide text-gold-text uppercase">
                  {t("accueil.inedites_exclusif")}
                </span>
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                {t("accueil.inedites_texte", { site: SITE_NAME })}
              </p>
            </div>
            <span className="flex shrink-0 items-center gap-1.5 text-sm font-medium text-gold-text">
              {t("accueil.explorer")}
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
        <h2 className="font-display text-xl font-semibold">{t("accueil.pourquoi_titre", { site: SITE_NAME })}</h2>
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
          {t("accueil.pourquoi_texte", { site: SITE_NAME })}
        </p>
        <div className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-border bg-card p-5">
            <span className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <Target className="size-5" />
            </span>
            <h3 className="mt-3 font-display text-base font-semibold">{t("accueil.avantage1_titre")}</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              {t("accueil.avantage1_texte")}
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-card p-5">
            <span className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <GraduationCap className="size-5" />
            </span>
            <h3 className="mt-3 font-display text-base font-semibold">{t("accueil.avantage2_titre")}</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              {t("accueil.avantage2_texte")}
            </p>
          </div>
          <div className="rounded-2xl border border-border bg-card p-5">
            <span className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <TrendingUp className="size-5" />
            </span>
            <h3 className="mt-3 font-display text-base font-semibold">{t("accueil.avantage3_titre")}</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              {t("accueil.avantage3_texte")}
            </p>
          </div>
          <div className="rounded-2xl border border-gold/30 bg-gold/5 p-5">
            <span className="flex size-10 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
              <Crown className="size-5" />
            </span>
            <h3 className="mt-3 font-display text-base font-semibold">{t("accueil.avantage4_titre")}</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              {t("accueil.avantage4_texte")}
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
              <span className="flex items-center gap-1.5 rounded-full bg-gold/15 px-3 py-1 text-xs font-semibold text-gold-text">
                <Crown className="size-3.5" />
                {t("accueil.vedette_badge")}
              </span>
              {inediteVedette.duree_minutes && (
                <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Clock className="size-3.5" />
                  {t("accueil.vedette_chrono", { n: inediteVedette.duree_minutes })}
                </span>
              )}
            </div>
            <h2 className="mt-3 font-display text-xl font-semibold">{inediteVedette.title}</h2>
            <p className="mt-1 max-w-2xl text-sm text-muted-foreground">
              {t("accueil.vedette_texte", { site: SITE_NAME })}
            </p>
            <div className="mt-5 rounded-xl border border-border bg-card p-5 sm:p-6">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gold-text">{t("accueil.apercu")}</p>
              <div className="prose prose-neutral max-w-none text-sm dark:prose-invert prose-headings:font-display">
                <EpreuveMarkdownLazy markdown={inediteVedette.apercu_enonce_markdown} />
              </div>
            </div>
            <div className="mt-4 flex flex-wrap justify-center gap-3">
              <Button asChild>
                <Link to={epreuveInediteDetailPath(country ?? "", inediteVedette.slug ?? inediteVedette.id)}>
                  {t("accueil.vedette_decouvrir")}
                  <ArrowRight />
                </Link>
              </Button>
              {/* La vedette n'est qu'une parmi d'autres (voir inediteRecenteData.count) -
                  sans ce second lien, un visiteur convaincu par l'aperçu n'avait aucun
                  moyen de savoir que d'autres inédites existent pour d'autres matières. */}
              <Button asChild variant="outline">
                <Link to={`${epreuvesListPath(country ?? "")}?${requeteInedites(cursusAccueil)}`}>
                  {inediteRecenteData && inediteRecenteData.count > 1
                    ? t("accueil.vedette_voir_n", { n: inediteRecenteData.count })
                    : t("accueil.vedette_voir_toutes")}
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
              <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-gold/15 text-gold-text">
                <Crown className="size-5" />
              </span>
              <div className="flex-1">
                <h2 className="font-display text-base font-semibold">{t("accueil.repli_titre")}</h2>
                <p className="mt-0.5 text-sm text-muted-foreground">
                  {t("accueil.repli_texte", { site: SITE_NAME })}
                </p>
              </div>
              <Button asChild>
                <Link to={`${epreuvesListPath(country ?? "")}?${requeteInedites(cursusAccueil)}`}>
                  {t("accueil.repli_bouton")}
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
            <h2 className="font-display text-2xl font-semibold">{t("accueil.pret_titre")}</h2>
            <p className="mx-auto mt-2 max-w-xl text-muted-foreground">
              {t("accueil.pret_texte", {
                prix: formatAmount(PRIX_ABONNEMENT_FCFA),
                prix_sup: formatAmount(PRIX_ENFANT_SUPPLEMENTAIRE_FCFA),
              })}
            </p>
            <div className="mt-5 flex justify-center">
              <Button size="lg" asChild>
                <Link to="/tarifs">
                  {t("accueil.voir_prix")}
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
