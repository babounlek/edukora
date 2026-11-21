import { useEffect, useState, type ReactNode } from "react"
import { Link, Navigate, useParams, useSearchParams } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { ArrowRight, BookOpen, Clock, Crown, GraduationCap, Layers, TrendingUp } from "lucide-react"

import {
  getAccueilVitrine,
  getEpreuveInedite,
  getMyProgression,
  readEpreuve,
} from "@/api/endpoints"
import { trackEvent } from "@/lib/analytics"
import { nomPays } from "@/lib/pays"
import { examLevelsFor, joinExamLevelsProse, libelleCursus } from "@/lib/cursus"
import { langueDeListe } from "@/lib/discipline"
import { langueCourante, t, tn, useI18n } from "@/lib/i18n"
import { useCursusListe } from "@/lib/cursusLangue"
import { exempleDuCursus, extraireExempleCorrige } from "@/lib/exempleCorrige"
import { PARAM_VOIR_TOUT } from "@/lib/filtreCursus"
import { libelleEnteteExercice } from "@/lib/libellesEpreuve"
import { PRIX_MOIS_FCFA } from "@/lib/tarifs"
import { SectionParents } from "@/components/SectionParents"
import { FaqAccueil } from "@/components/FaqAccueil"
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
import { BandeauCampagne } from "@/components/BandeauCampagne"
import { useCampagne } from "@/lib/campagne"
import { Button } from "@/components/ui/button"
import { SocialProofSection } from "@/components/SocialProofSection"
import { AccueilDecouverte } from "@/components/AccueilDecouverte"
import { BarreCommencer } from "@/components/BarreCommencer"
import { InviteInstallation } from "@/components/InviteInstallation"
import { AccueilEleve } from "@/components/AccueilEleve"
import { InviteAutreSousSystemeDuPays } from "@/components/InviteAutreSousSysteme"
import { requeteInedites, useCursusAccueil, useInedites } from "@/lib/cursusAccueil"
import { PremiereSeance } from "@/components/PremiereSeance"
import { SqueletteDePage } from "@/components/RouteFallback"
import { accueilEleveProbable, marquerAccueilEleve, oublierAccueilEleve } from "@/lib/indiceAccueil"
import { useInstallationPossible } from "@/lib/installation"
import { seancesJouees } from "@/lib/seancesGratuites"

// Clés de filtre reconnues par /epreuves (voir EpreuvesListPage) - un lien déjà en
// circulation qui les porte encore sur cette URL (recherche sauvegardée en session,
// lien partagé, l'onboarding qui pointait ici avant la scission accueil/catalogue)
// doit continuer à filtrer, pas silencieusement retomber sur l'accueil nu.
const FILTER_PARAM_KEYS = ["subject", "cursus", "origine", "nature", "gratuit", "search"]

/** Les boutons mesurés de la vitrine : vocabulaire fermé, comme les noms d'évènements. */
type CibleAccueil =
  | "campagne"
  | "corrige_gratuit"
  | "themes"
  | "exemple_corrige"
  | "inedite_vedette"
  | "inedites_liste"
  | "prix"

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
    // Sur un téléphone, le numéro passe à gauche du texte au lieu de prendre sa propre ligne : les trois étapes
    // empilées faisaient 841 px (audit des accueils, 2026-11-21). À partir de `sm`, la carte d'avant, en colonne.
    <div className="flex gap-3 rounded-2xl border border-border bg-card p-4 sm:flex-col sm:gap-2 sm:p-5">
      <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary/10 font-display font-semibold text-primary">
        {numero}
      </span>
      <div className="flex min-w-0 flex-col gap-1 sm:gap-2">
        <h3 className="font-display text-lg font-semibold">{titre}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  )
}

/** Les matières préférées pour l'épreuve inédite montrée à un visiteur qui n'a pas dit son examen (voir plus bas). */
const MATIERES_VEDETTE = [/^MATH/, /^FRAN/]

/**
 * La page vitrine : le hero, les chiffres, l'exemple de corrigé, les inédites, la
 * preuve sociale. Ce que voient un visiteur anonyme et un robot d'indexation.
 *
 * `decouverte` : un élève connecté qui n'a pas encore d'abonnement. C'est toujours sa page de conversion, mais plus
 * celle d'un inconnu : sa carte « Aujourd'hui » (voir AccueilDecouverte) remplace le hero, et il ne garde de la vitrine
 * que les preuves (extrait de corrigé, épreuve inédite de son examen, avis) et le rappel du prix. La promesse,
 * « Comment ça marche », le bloc parent et les questions fréquentes ne lui sont plus montrés (audit des accueils,
 * 2026-11-21 : 8,2 écrans, la seule action possible au troisième).
 *
 * Un élève ABONNÉ voit AccueilEleve à la place (voir CataloguePage en bas de
 * fichier) : plus aucun argumentaire, seulement ses affaires.
 */
function CatalogueVitrine({ decouverte = false }: { decouverte?: boolean }) {
  // S'abonne au changement de langue : les `t(...)` ci-dessous se relisent à chaque bascule.
  useI18n()
  const { country } = useParams<{ country: string }>()
  const { countries } = useCountry()
  const countryLabel = nomPays(countries, country)
  const { isAuthenticated } = useAuth()
  const campagne = useCampagne()
  const [searchParams] = useSearchParams()
  // Lu une fois au montage : a-t-il déjà joué une séance gratuite sur cet appareil (voir lib/seancesGratuites) ?
  const [aDejaJoue] = useState(() => seancesJouees().size > 0)
  const installationPossible = useInstallationPossible()

  // Mesure des clics de la vitrine (audit de l'accueil du 2026-11-15, R5) : seul le nom du bouton part (`cible`),
  // jamais de texte ni d'identité - voir analytics.models.EventName.ACCUEIL_BOUTON_CLIC. Sans elle, impossible de
  // savoir lequel des boutons du hero sert, ni si quelqu'un descend jusqu'aux prix.
  const mesurer = (cible: CibleAccueil) => () => trackEvent("accueil_bouton_clic", { cible })

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
    // ?pos= : l'emplacement du lien dans le PDF (voir EpreuveDetailPage et backend catalog.pdf_fin).
    trackEvent("pdf_fiche_sujet_landing", { country, position: searchParams.get("pos") ?? "" })
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

  // Les trois chiffres du hero et les témoignages, en UN appel (audit de l'accueil du 2026-11-15, R9). La page demandait
  // la liste des épreuves, celle des cours et celle des matières pour n'en lire que le total, puis les témoignages. Les
  // totaux restent ceux des listes, dans la langue de l'interface : le serveur interroge les mêmes vues (voir
  // catalog.accueil_api), donc une puce « N cours » mène toujours à une liste qui affiche N.
  const langueAccueil = langueDeListe("", false)
  const { data: accueil } = useQuery({
    queryKey: ["accueil-vitrine", country, langueAccueil],
    queryFn: ({ signal }) => getAccueilVitrine(country, langueAccueil, signal),
    enabled: Boolean(country) && !hasLegacyFilters,
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
  const examenServi = cursusList?.find((c) => c.id === cursusAccueil)
  // Toujours un corrigé de l'examen déclaré, ou rien : null tant que la liste des examens charge (sinon l'exemple par
  // défaut, celui d'un autre examen, clignoterait avant le bon) et pour un examen sans épreuve gratuite.
  const exemple = cursusAccueil === undefined ? null : exempleDuCursus(langueCourante(), examenServi)
  const { data: exempleContent } = useQuery({
    queryKey: ["epreuve-exemple-corrige", exemple?.slug],
    queryFn: () => readEpreuve(exemple!.slug),
    enabled: !hasLegacyFilters && exemple !== null,
    retry: false,
  })
  // Le corrigé à montrer (question 1 seule ou exercice entier, selon l'exemple) : voir extraireExempleCorrige.
  const extrait = extraireExempleCorrige(exempleContent, exemple)
  const exempleExercice = extrait?.exercice
  const exempleCorrigeQ1 = extrait?.corrigeMarkdown


  // Épreuve inédite mise en avant, pour la section "preuve" dédiée plus bas - jamais un
  // slug codé en dur (contrairement à EXEMPLES_CORRIGE) : la plus récente pour ce
  // pays, redécouverte à chaque chargement, donc jamais périmée si le contenu change.
  // Restreinte au cursus déclaré (compte ou onboarding) quand il y en a un : voir
  // useInedites.
  const { data: inediteRecenteData } = useInedites(country ?? "", cursusAccueil, !hasLegacyFilters)
  // Sans examen choisi, la plus récente du pays peut être d'une matière que peu d'élèves passent (« Travail manuel »
  // le jour de l'audit des accueils, 2026-11-21) : seul exemple du produit payant sur la page, elle est alors prise
  // parmi les récentes dans une matière que tous ont, mathématiques puis français. Examen choisi : la plus récente.
  const ineditesRecentes = inediteRecenteData?.results ?? []
  const inediteMontree =
    (cursusAccueil == null
      ? MATIERES_VEDETTE.map((motif) => ineditesRecentes.find((e) => motif.test(e.subject?.code ?? ""))).find(Boolean)
      : undefined) ?? ineditesRecentes[0]
  const inediteVedetteId = inediteMontree?.slug ?? inediteMontree?.id
  // Les inédites de tout le pays (même clé de cache que l'en-tête), demandées seulement quand l'examen déclaré n'en a aucune :
  // c'est ce qui permet de proposer « celles des autres examens » sans promettre une liste vide.
  const aucuneInedite = examenServi != null && inediteRecenteData?.count === 0
  const { data: ineditesDuPays } = useInedites(country ?? "", null, aucuneInedite && !hasLegacyFilters)

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

  useSeo(
    // Un élève connecté sans abonnement voit sa page « Aujourd'hui » (voir AccueilDecouverte) : même titre que celle
    // d'un abonné, et jamais indexée - les robots n'ont pas de session, ils voient la vitrine.
    decouverte
      ? { title: t("accueil.seo_eleve"), description: t("accueil.seo_eleve_description"), noindex: true }
      : {
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
        },
  )

  if (hasLegacyFilters) {
    return <Navigate to={`${epreuvesListPath(country ?? "")}?${searchParams.toString()}`} replace />
  }

  return (
    // `accueil-vitrine` : repère lu par le tutoriel du visiteur, qui attend que cette page soit montée pour savoir si
    // la carte « première séance » est à l'écran (voir lib/guides/contenu.ts).
    <div data-guide="accueil-vitrine">
      {/* Un élève connecté sans abonnement : sa carte « Aujourd'hui » (séance gratuite, points, séance complète
          fermée) à la place du hero. La vitrine reste entière pour un visiteur comme pour un robot : /cm est la page
          la plus indexée du site. */}
      {decouverte && <AccueilDecouverte country={country ?? ""} />}
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
      {/* L'offre promotionnelle en haut de la vitrine, avant le premier écran de défilement : un visiteur
          qui ne descend pas jusqu'au bloc « Prêt à commencer ? » doit quand même la voir. Cliquable vers /tarifs. */}
      {campagne && (
        <div className="mx-auto max-w-5xl px-4 pt-4 sm:px-6">
          <Link to="/tarifs" onClick={mesurer("campagne")} className="block transition-opacity hover:opacity-90">
            <BandeauCampagne campagne={campagne} prix={campagne.prix} prixReference={campagne.prix_reference} />
          </Link>
        </div>
      )}
      {/* Le hero du visiteur : la promesse, la carte « première séance », les chiffres. Pas pour un élève connecté sans
          abonnement, qui a sa carte au-dessus et connaît déjà la promesse (audit des accueils, 2026-11-21). */}
      {!decouverte && (
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
        {/* Trois blocs dans une grille. Sur un téléphone ils se suivent : promesse, carte, liens - la carte arrive donc
            dès le premier écran, avant les liens secondaires. Sur un écran large, la carte occupe la colonne de droite
            et les deux blocs de texte s'empilent à gauche.
            pb-8 : le bandeau de chiffres qui suit appartient au hero. */}
        <div className="relative mx-auto grid max-w-5xl gap-x-10 gap-y-6 px-4 pb-8 pt-10 sm:px-6 sm:pt-14 md:grid-cols-[1.1fr_1fr] md:items-center">
          <div className="md:col-start-1 md:row-start-1 md:self-end">
            {/* L'examen choisi se lit et se change dans la carte (voir PremiereSeance) : l'accroche garde les examens
                du pays, pour un visiteur neuf comme pour un robot. */}
            <p className="mb-2 font-display text-sm italic text-primary">
              {examLevelsHero}{countryLabel ? ` - ${countryLabel}` : ""}
            </p>
            {/* La promesse est celle d'un coach (« on te dit quoi réviser »), pas d'une bibliothèque : le volume du
                corpus vient après, comme preuve. */}
            <h1 className="max-w-xl font-display text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
              {t("accueil.hero_titre_debut")}{" "}
              <span className="text-primary">{t("accueil.hero_titre_accent")}</span>.
            </h1>
            <p className="mt-4 max-w-lg text-muted-foreground">
              {t("accueil.hero_texte")}
            </p>
          </div>

          {/* L'action principale du hero (audit de l'accueil du 2026-11-15, R6 et R7) : choisir son examen, puis lancer
              une vraie première séance sans compte. Elle remplace la photo d'illustration et les deux boutons qui
              menaient à des listes. */}
          <div className="md:col-start-2 md:row-span-2 md:row-start-1">
            <PremiereSeance country={country ?? ""} />
          </div>

          <div className="md:col-start-1 md:row-start-2 md:self-start">
            {/* Le prix n'apparaissait qu'au septième écran, alors que c'est un argument (audit de l'accueil du
                2026-11-15, R2) : une ligne dit ce qui est gratuit et ce que coûte la suite. */}
            <p className="max-w-lg text-sm text-muted-foreground">
              {t("accueil.hero_reassurance", { prix: formatAmount(PRIX_MOIS_FCFA) })}
            </p>
            {/* Porte secondaire : lire d'abord, pour qui ne veut pas d'un quiz. Bouton de contour, la carte porte
                le seul bouton plein du hero. */}
            <div className="mt-4 flex flex-wrap items-center gap-3">
              <Button variant="outline" size="lg" asChild className="border-primary/40 text-primary hover:text-primary">
                <Link to={`${epreuvesListPath(country ?? "")}?gratuit=true`} onClick={mesurer("corrige_gratuit")}>
                  {t("accueil.cta_corrige_gratuit")}
                  <ArrowRight />
                </Link>
              </Button>
            </div>
            <Link
              to={themesFrequentsPath(country ?? "")}
              onClick={mesurer("themes")}
              className="mt-3 flex w-fit items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
            >
              <TrendingUp className="size-3.5 text-primary" />
              {t("accueil.themes_frequents")}
              <ArrowRight className="size-3" />
            </Link>
            {/* Pour qui prépare l'autre sous-système (le GCE sur la version française, le BAC sur
                l'anglaise) : la page ne propose que les examens de sa langue. Variante compacte : une seule phrase,
                là où la ligne doublée en deux langues prenait trois lignes sur un téléphone. */}
            <InviteAutreSousSystemeDuPays variante="compacte" className="mt-3" />
          </div>
        </div>

        {/* La page n'affichait aucun chiffre, alors que sa volumétrie est son argument
            le plus crédible - et le seul qu'un concurrent ne peut pas recopier. Tous
            viennent de l'API, aucun n'est écrit en dur.
            Bandeau pleine largeur SOUS la grille à deux colonnes, et non dans sa
            colonne de gauche : là, les trois puces n'avaient que ~550 px et se
            cassaient en 2 + 1, ce qui se lisait comme un accident de mise en page.
            Constaté à l'écran, pas déduit. Ce bandeau comble aussi la couture un peu
            vide entre le hero et la section suivante. */}
        {accueil && (
          <div className="relative mx-auto flex max-w-5xl flex-wrap gap-2 px-4 pb-14 sm:px-6">
            <StatChip
              icon={<BookOpen className="size-3.5 text-primary" />}
              valeur={formatAmount(accueil.epreuves)}
              libelle={tn("accueil.stat_epreuves", accueil.epreuves > 1 ? 2 : 1)}
            />
            <StatChip
              icon={<GraduationCap className="size-3.5 text-gold-text" />}
              valeur={formatAmount(accueil.cours)}
              libelle={t("accueil.stat_cours")}
            />
            {accueil.matieres > 0 && (
              <StatChip
                icon={<Layers className="size-3.5 text-success" />}
                valeur={String(accueil.matieres)}
                libelle={tn("accueil.stat_matieres", accueil.matieres > 1 ? 2 : 1)}
              />
            )}
          </div>
        )}
      </section>
      )}

      {/* Le visiteur qui revient après une séance gratuite : garder le site sur son téléphone est le rappel le moins
          cher qui soit, et rien d'autre ne le fait revenir (ni compte, ni rappel). L'invitation n'existait que sur le
          résultat d'un quiz ; elle se tait pour de bon dès qu'il a répondu (voir lib/installation). */}
      {!decouverte && !isAuthenticated && aDejaJoue && installationPossible && (
        <div className="mx-auto max-w-5xl px-4 pt-6 sm:px-6">
          <InviteInstallation />
        </div>
      )}

      {/* La promesse du H1 ("la méthode qui t'apprend à réussir") était affirmée,
          jamais montrée. Extrait réel d'un corrigé publié (voir EXEMPLES_CORRIGE),
          rendu par le même composant que la lecture complète (EpreuveMarkdown) - donc
          le même KaTeX, pas une capture d'écran ni un mock. Disparaît silencieusement
          si le slug ne charge pas (même patron que SocialProofSection/EpreuveRail). */}
      {exemple && exempleExercice && exempleCorrigeQ1 && (
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
            {/* Borné en hauteur, avec un fondu : entier, l'extrait faisait 1 374 px sur un téléphone, 1,7 écran de calcul
                avant la section suivante (audit des accueils, 2026-11-21). Ce qui reste montre l'énoncé, le rappel de
                méthode et les premières étapes ; le bouton juste dessous ouvre le corrigé complet, gratuit. Le texte
                coupé reste dans la page pour les lecteurs d'écran. */}
            <div className="relative max-h-[26rem] overflow-hidden">
              <div className="prose prose-neutral max-w-none text-sm dark:prose-invert prose-headings:font-display">
                <EpreuveMarkdownLazy markdown={exempleCorrigeQ1} />
              </div>
              <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-card to-transparent" />
            </div>
            <div className="mt-4 flex justify-center border-t border-border pt-4">
              <Button asChild variant="outline">
                <Link to={epreuveReaderPath(country ?? "", exemple.slug)} onClick={mesurer("exemple_corrige")}>
                  {t("accueil.lire_corrige_complet")}
                  <ArrowRight />
                </Link>
              </Button>
            </div>
          </div>
        </section>
      )}

      {/* « Comment ça marche » s'adresse à qui ne connaît pas le produit : un élève connecté a déjà dit son examen et
          sa carte lui montre la séance. Pour lui, seulement l'espace que cette section laissait avant les inédites. */}
      {decouverte && <div aria-hidden="true" className="h-6" />}
      {!decouverte && (
      <section className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
        {/* Le récit du plan, à la place d'une grille de quatre portes (Épreuves,
            Cours, Parcours, Quiz). Cette grille décrivait notre modèle de données -
            deux types de documents et deux outils - et laissait l'élève composer son
            itinéraire lui-même, exactement ce dont la séance du jour le décharge. Elle
            contredisait aussi la navigation, réduite depuis à trois entrées.
            Les quatre destinations restent atteignables : "Réviser" dans le menu, et
            l'encart Épreuves Inédites plus bas pour le produit payant. */}
        <h2 className="font-display text-xl font-semibold">{t("accueil.comment_titre")}</h2>
        {/* Ce qui distingue le produit des annales gratuites, dit une fois, ici : la grille « Pourquoi EduKora ? » qui
            suivait redisait ces trois étapes en quatre cartes (audit de l'accueil du 2026-11-15, R4). */}
        <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{t("accueil.pourquoi_texte", { site: SITE_NAME })}</p>
        <div className="mt-4 grid gap-3 sm:grid-cols-3 sm:gap-5">
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
        {/* L'examen déclaré n'a aucune inédite : plutôt que de faire disparaître le bloc, on le dit (sinon le choix semble
            ignoré), et on ouvre celles des autres examens quand il y en a. `tout=1` : sans lui, la liste se réduirait
            aussitôt à l'examen déclaré, c'est-à-dire à rien (voir useFiltreCursusParDefaut). */}
        {aucuneInedite && examenServi && (
          <p className="mt-5 flex flex-wrap items-center gap-x-2 gap-y-1 rounded-2xl border border-dashed border-border px-5 py-4 text-sm text-muted-foreground">
            <Crown className="size-4 shrink-0 text-gold-text" aria-hidden="true" />
            <span>{t("accueil.inedites_aucune", { cursus: libelleCursus(examenServi) })}</span>
            {ineditesDuPays && ineditesDuPays.count > 0 && (
              <Link
                to={`${epreuvesListPath(country ?? "")}?origine=INEDITE&${PARAM_VOIR_TOUT}=1`}
                className="underline underline-offset-4 transition-colors hover:text-primary"
              >
                {t("accueil.inedites_autres")}
              </Link>
            )}
          </p>
        )}
      </section>
      )}

      {/* Les épreuves inédites n'ont plus qu'une présentation sur cette page : l'encart ci-dessous, avec une vraie
          question (ou son repli compact). Le bandeau « Exclusif » et la carte « Tu te testes sur l'inconnu » qui les
          annonçaient deux fois de plus ont été retirés (audit de l'accueil du 2026-11-15, R4). */}
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
                <Link
                  to={epreuveInediteDetailPath(country ?? "", inediteVedette.slug ?? inediteVedette.id)}
                  onClick={mesurer("inedite_vedette")}
                >
                  {t("accueil.vedette_decouvrir")}
                  <ArrowRight />
                </Link>
              </Button>
              {/* La vedette n'est qu'une parmi d'autres (voir inediteRecenteData.count) -
                  sans ce second lien, un visiteur convaincu par l'aperçu n'avait aucun
                  moyen de savoir que d'autres inédites existent pour d'autres matières. */}
              <Button asChild variant="outline">
                <Link to={`${epreuvesListPath(country ?? "")}?${requeteInedites(cursusAccueil)}`} onClick={mesurer("inedites_liste")}>
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
                <Link to={`${epreuvesListPath(country ?? "")}?${requeteInedites(cursusAccueil)}`} onClick={mesurer("inedites_liste")}>
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
      <SocialProofSection fournis={accueil ? accueil.temoignages : null} />

      {/* Le parent qui paie : voir SectionParents (audit du 2026-11-12, UX-03). Pas pour un élève connecté : sa carte
          porte « Montrer à mes parents », qui leur envoie le prix et le moyen de payer. */}
      {!decouverte && <SectionParents />}

      {/* Les questions qu'on se pose avant d'essayer : voir FaqAccueil (audit de l'accueil du 2026-11-15, R10). Un élève
          connecté a déjà essayé (« Faut-il créer un compte ? ») ; le centre d'aide reste dans l'en-tête. */}
      {!decouverte && <FaqAccueil />}

      {/* Dernière section avant le footer (audit UX externe, 2026-09-04) : la page
          démontrait la valeur du produit (démo de corrigé, inédites, preuve sociale)
          sans jamais pousser explicitement vers l'abonnement - un visiteur convaincu
          n'avait que le menu du header pour trouver /tarifs. Pas de prix ici : ils
          dépendent du cursus (voir PricingPage/Plan.effective_price), les répéter en
          dur ici les désynchroniserait silencieusement de la vraie grille. */}
      {/* `data-fin-vitrine` : repère de la barre « Commencer » du visiteur, qui s'efface en arrivant ici (voir BarreCommencer). */}
      <section data-fin-vitrine className="mx-auto max-w-5xl px-4 pb-14 sm:px-6">
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
              {t("accueil.pret_texte", { prix: formatAmount(PRIX_MOIS_FCFA) })}
            </p>
            {campagne && (
              <BandeauCampagne
                campagne={campagne}
                prix={campagne.prix}
                prixReference={campagne.prix_reference}
                className="mx-auto mt-4 max-w-xl justify-center text-left"
              />
            )}
            <div className="mt-5 flex justify-center">
              <Button size="lg" asChild>
                <Link to="/tarifs" onClick={mesurer("prix")}>
                  {t("accueil.voir_prix")}
                  <ArrowRight />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
      {/* Sur un téléphone, le bouton « Commencer » suit le visiteur entre la carte du hero et ce dernier bloc. Pas pour
          un élève connecté sans abonnement : sa carte est en tête et la barre d'onglets occupe déjà le bas de l'écran. */}
      {!decouverte && <BarreCommencer country={country ?? ""} />}
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
 *   - élève SANS abonnement  -> sa carte « Aujourd'hui » (séance gratuite, points,
 *                               séance complète fermée), puis les preuves et le prix :
 *                               c'est sa page de conversion (voir `decouverte`) ;
 *   - élève ABONNÉ           -> ses affaires, et rien d'autre.
 *
 * Le branchement vit ici, dans un composant qui n'appelle qu'un seul hook, et pas
 * dans un `return` anticipé au milieu de la vitrine : les quinze requêtes du
 * catalogue ne partent ainsi jamais pour un élève qui ne verra pas cette page.
 *
 * Pendant que l'authentification se résout (un aller-retour de rafraîchissement au
 * démarrage), c'est la vitrine qui s'affiche. C'est volontaire : c'est le seul défaut
 * sûr pour un robot ou un visiteur, qui sont la majorité des arrivées sur cette URL.
 * Un élève abonné la verrait donc un instant avant sa page : un indice mémorisé côté navigateur l'évite (voir plus bas).
 */
export function CataloguePage() {
  const { isAuthenticated, isLoading, user } = useAuth()
  const { country } = useParams<{ country: string }>()
  const aUnExamen = Boolean(isAuthenticated && user?.cursus_prepare)
  const abonne = aUnExamen && Boolean(user?.a_un_abonnement_actif)
  // Connecté, examen déclaré, pas d'abonnement en cours : la vitrine, mais avec sa carte « Aujourd'hui » à la place
  // du hero et sans l'argumentaire écrit pour un inconnu (voir AccueilDecouverte).
  const decouverte = aUnExamen && !abonne

  // L'indice mémorisé annoncé plus haut (voir lib/indiceAccueil) : posé quand l'accueil d'un élève s'affiche, abonné ou
  // non, retiré dès que la session est connue et que ce n'est pas un élève. Tant que la session se retrouve, un élève
  // probable voit un squelette et non le hero du visiteur ; un visiteur ou un robot, qui n'ont jamais l'indice, voient
  // la vitrine d'emblée.
  useEffect(() => {
    if (aUnExamen) marquerAccueilEleve()
    else if (!isLoading) oublierAccueilEleve()
  }, [aUnExamen, isLoading])

  if (abonne) return <AccueilEleve country={country ?? ""} />
  if (isLoading && accueilEleveProbable()) return <SqueletteDePage />
  return <CatalogueVitrine decouverte={decouverte} />
}
