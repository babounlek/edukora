import { useCallback, useEffect, useState } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Check, ChevronDown, CircleHelp, GraduationCap, Globe, History, LogOut, Menu, Receipt, Search, Sparkles, User, UserCircle } from "lucide-react"

import { listEpreuves } from "@/api/endpoints"
import { useAuth } from "@/context/AuthContext"
import { useCountry } from "@/context/CountryContext"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ThemeToggle } from "@/components/ThemeToggle"
import { ETAT_FOCUS_RECHERCHE } from "@/lib/recherche"
import { libellePays, nomPays } from "@/lib/pays"
import { useRaccourciRecherche } from "@/lib/useRaccourciRecherche"
import { CompteAReboursBadge, formatCursus } from "@/components/CompteAReboursBadge"
import { useCursusAbonnes } from "@/lib/changerCursusPrepare"
import { useProfils, useChangerProfilActif } from "@/lib/changerProfilActif"
import { cn } from "@/lib/utils"
import { ineditesNouvelles, marquerIneditesVues, useIneditesVues } from "@/lib/ineditesVues"
import { SITE_NAME } from "@/lib/site"
import { ouvrirCentre } from "@/lib/guides/etat"
import { langueCourante, localeCourante, useI18n } from "@/lib/i18n"
import { SelecteurLangue, useSynchroLangueCompte } from "@/components/SelecteurLangue"
import { catalogueHomePath, coursListPath, epreuvesListPath, recherchePath, themesFrequentsPath } from "@/lib/countryPath"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Sheet, SheetContent, SheetDescription, SheetTitle, SheetTrigger } from "@/components/ui/sheet"

/**
 * Le menu du compte : "Mon compte" restait le seul point d'entrée vers les accès, l'historique et
 * les paiements, obligeant à charger toute la page /compte pour y accéder - ce menu déroulant les
 * rend atteignables en un clic depuis n'importe quelle page, et allège /compte d'autant (voir
 * AccountPage, dont les sections "Mes accès", "Dernières tentatives" et "Ce que j'ai lu" ont
 * déménagé vers /mes-acces et /historique).
 */
function AccountMenu() {
  const { user, logout } = useAuth()
  const { country } = useCountry()
  const navigate = useNavigate()
  const cursusAbonnes = useCursusAbonnes()
  const profils = useProfils()
  const changerProfil = useChangerProfilActif()
  const { t } = useI18n()
  // L'abonnement du profil actif : nulle part ailleurs que dans « Mes accès » (page de parent) l'élève ne voyait qu'il était
  // abonné ni jusqu'à quand (test élève Gogo). Une ligne en tête du menu, sans lien : de quoi se rassurer.
  const famille = profils.length > 1 && !user?.session_restreinte
  const abonnementActif = cursusAbonnes.find(
    (sub) => sub.profil.id === user?.profil_actif?.id && sub.cursus.id === user?.cursus_prepare?.id,
  )

  function handleLogout() {
    logout()
    // Différé plutôt qu'appelé juste après logout() : ce menu est désormais accessible
    // depuis n'importe quelle page protégée (Mes paiements, Mon compte...), qui a
    // chacune son propre useEffect de garde redirigeant vers /connexion dès que
    // isAuthenticated passe à false. Cet effet se déclenche APRES ce gestionnaire
    // (React ne les exécute qu'une fois le rendu commité), donc un navigate() appelé
    // ici - avant ou après logout() - se fait systématiquement écraser par le sien.
    // Le seul ordre qui gagne est un navigate() planifié après lui, d'où ce setTimeout.
    setTimeout(() => navigate(catalogueHomePath(country), { replace: true }), 0)
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="flex items-center gap-1.5">
          <UserCircle className="size-4 shrink-0" />
          {/* Tronqué sur petit écran : un nom complet un peu long (le champ est libre)
              repoussait sinon la barre au-delà de la largeur de l'écran. */}
          <span className="max-w-[7.5rem] truncate sm:max-w-none">
            {user?.profil_actif?.prenom || user?.full_name || user?.pseudo || user?.phone_number}
          </span>
          <ChevronDown className="size-3.5 shrink-0 opacity-60" aria-hidden="true" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        {abonnementActif && (
          <>
            <DropdownMenuLabel className="font-normal text-muted-foreground">
              {t("compte.abonnement_jusqua", {
                cursus: formatCursus(abonnementActif.cursus),
                date: new Date(abonnementActif.expires_at).toLocaleDateString(localeCourante(), {
                  day: "numeric", month: "long", year: "numeric",
                }),
              })}
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
          </>
        )}
        {/* Seulement si le compte a déjà déclaré 2+ enfants : sinon il n'y a rien à
            basculer, profil_actif retombe silencieusement sur l'unique profil. */}
        {profils.length > 1 && !user?.session_restreinte && (
          <>
            <DropdownMenuLabel>{t("compte.changer_enfant")}</DropdownMenuLabel>
            {profils.map((profil) => {
              const actif = profil.id === user?.profil_actif?.id
              return (
                <DropdownMenuItem
                  key={profil.id}
                  disabled={changerProfil.isPending}
                  onSelect={() => {
                    if (!actif) changerProfil.mutate({ profilId: profil.id, prenom: profil.prenom })
                  }}
                >
                  {actif ? <Check className="text-primary" /> : <User />}
                  {profil.prenom || t("compte.profil_sans_nom")}
                </DropdownMenuItem>
              )
            })}
            <DropdownMenuSeparator />
          </>
        )}
        {/* Seulement si le compte a deux abonnements actifs ou plus : sinon il n'y a
            rien à basculer, la bascule silencieuse (voir changerCursusPrepare) suffit.
            Chaque entrée est un ABONNEMENT (profil + cursus), pas un simple cursus :
            deux profils peuvent préparer le même examen (voir useCursusAbonnes) -
            cliquer doit donc basculer sur CE couple précis (activerProfil avec
            cursusId), jamais sur le profil seul suivi d'un réalignement générique qui
            pourrait retomber sur un AUTRE cursus de ce même profil (régression
            signalée : "un enfant avec un cursus qui n'est pas le sien"). */}
        {cursusAbonnes.length > 1 && !user?.session_restreinte && (
          <>
            <DropdownMenuLabel>{t("compte.examen_prepare")}</DropdownMenuLabel>
            {cursusAbonnes.map((sub) => {
              const actif = sub.cursus.id === user?.cursus_prepare?.id && sub.profil.id === user?.profil_actif?.id
              return (
                <DropdownMenuItem
                  key={sub.id}
                  disabled={changerProfil.isPending}
                  onSelect={() => {
                    if (!actif) changerProfil.mutate({ profilId: sub.profil.id, cursusId: sub.cursus.id })
                  }}
                >
                  {actif ? <Check className="text-primary" /> : <GraduationCap />}
                  {formatCursus(sub.cursus)} ({sub.profil.prenom})
                </DropdownMenuItem>
              )
            })}
            <DropdownMenuSeparator />
          </>
        )}
        {/* Dans une famille, l'historique est celui de l'enfant actif ; compte, accès et paiements sont l'affaire du
            parent : un libellé les regroupe pour qu'un enfant sache de quel côté il se trouve (test élève Gogo, C-F3). */}
        {famille && (
          <>
            <DropdownMenuItem asChild>
              <Link to="/historique">
                <History />
                {t("compte.historique")}
              </Link>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuLabel>{t("compte.espace_parent")}</DropdownMenuLabel>
          </>
        )}
        <DropdownMenuItem asChild>
          <Link to="/compte">
            <UserCircle />
            {t("compte.mon_compte")}
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link to="/mes-acces">
            <Sparkles />
            {t("compte.mes_acces")}
          </Link>
        </DropdownMenuItem>
        {!famille && (
          <DropdownMenuItem asChild>
            <Link to="/historique">
              <History />
              {t("compte.historique")}
            </Link>
          </DropdownMenuItem>
        )}
        <DropdownMenuItem asChild>
          <Link to="/mes-paiements">
            <Receipt />
            {t("compte.paiements")}
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onSelect={handleLogout} className="text-destructive focus:text-destructive [&_svg]:text-destructive">
          <LogOut />
          {t("compte.deconnexion")}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

/**
 * `onNavigate` : appelé après un changement de pays, pour que l'exemplaire rendu
 * dans le menu mobile referme ce menu au lieu de laisser le visiteur devant un
 * panneau ouvert sur une page qui a déjà changé.
 * `dansLeMenu` : rendu à l'intérieur du menu mobile plutôt que dans la barre. La
 * contrainte de largeur y disparaît, le nom complet du pays est donc toujours
 * affiché - c'est dans la barre, et elle seule, qu'il faut se rabattre sur le code.
 */
function CountrySwitcher({ onNavigate, dansLeMenu = false }: { onNavigate?: () => void; dansLeMenu?: boolean }) {
  const { country, countries, setCountry } = useCountry()
  const navigate = useNavigate()
  const { t } = useI18n()

  // Un Country peut exister en base avant que du contenu réel n'y soit ingéré (voir
  // CountrySerializer.has_lessons côté backend) - ne proposer à la navigation que les
  // pays où il y a effectivement quelque chose à lire, pour ne jamais faire atterrir
  // un visiteur sur un catalogue vide.
  const browsableCountries = countries.filter((c) => c.has_lessons)

  function handleChange(code: string) {
    setCountry(code)
    navigate(catalogueHomePath(code))
    onNavigate?.()
  }

  if (browsableCountries.length === 0) {
    return (
      <span className="flex items-center gap-1 px-2 text-xs font-medium text-muted-foreground">
        <Globe className="size-3.5" />
        {country.toUpperCase()}
      </span>
    )
  }

  const currentLabel = nomPays(browsableCountries, country)

  return (
    <Select value={country} onValueChange={handleChange}>
      <SelectTrigger
        aria-label={t("pays.changer")}
        className={cn(
          "shrink-0 gap-1",
          dansLeMenu
            ? "h-10 flex-1 px-3 text-sm"
            : "h-9 w-[72px] px-2 text-xs sm:w-auto sm:max-w-[150px] sm:text-sm",
        )}
      >
        <Globe className="size-3.5 shrink-0 text-muted-foreground" />
        {/* Enfant explicite (pas le comportement par défaut de SelectValue) : replié,
            le visiteur doit voir clairement sur quel pays il navigue - le nom complet
            partout où la place le permet, le code ("CM") seulement dans la barre sur
            petit écran. La liste ouverte, elle, garde toujours les noms complets. */}
        <SelectValue>
          {dansLeMenu ? (
            <span className="truncate">{currentLabel ?? country.toUpperCase()}</span>
          ) : (
            <>
              <span className="sm:hidden">{country.toUpperCase()}</span>
              <span className="hidden truncate sm:inline">{currentLabel ?? country.toUpperCase()}</span>
            </>
          )}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {browsableCountries.map((c) => (
          <SelectItem key={c.id} value={c.code.toLowerCase()}>
            {libellePays(c.code, c.label)}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

export function Header() {
  const { isAuthenticated, isLoading: authLoading, user } = useAuth()
  // Même condition que CompteAReboursBadge, qui décide seul de s'afficher ou non - ici
  // uniquement pour savoir si la baseline doit lui laisser la place (voir plus bas).
  const aUnCompteARebours = Boolean(user?.compte_a_rebours && user.cursus_prepare)
  const { country } = useCountry()
  const { t } = useI18n()
  useSynchroLangueCompte()
  const { pathname, search } = useLocation()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  // « / » et Ctrl/⌘+K mènent à la page de recherche, champ sélectionné (voir RecherchePage).
  const navigate = useNavigate()
  const ouvrirRecherche = useCallback(
    () => navigate(recherchePath(country), { state: ETAT_FOCUS_RECHERCHE }),
    [navigate, country],
  )
  useRaccourciRecherche(ouvrirRecherche)

  const isTarifsSection = pathname.startsWith("/tarifs")
  const isParcoursSection = !isTarifsSection && pathname.startsWith("/parcours")
  const isCoursSection =
    !isTarifsSection && !isParcoursSection && (pathname === coursListPath(country) || pathname.startsWith("/cours"))
  const isEpreuvesSection =
    !isCoursSection &&
    !isTarifsSection &&
    !isParcoursSection &&
    (pathname === epreuvesListPath(country) || pathname.startsWith("/epreuves"))
  const isAccueil = pathname === catalogueHomePath(country) || pathname === `${catalogueHomePath(country)}/`
  // "Réviser" couvre les surfaces de révision (épreuves, cours, thèmes, quiz), qui
  // gardent chacune leur URL - seul le regroupement change, voir ReviserTabs.
  const isReviserSection =
    isEpreuvesSection ||
    isCoursSection ||
    pathname.startsWith(themesFrequentsPath(country)) ||
    pathname.startsWith(recherchePath(country)) ||
    pathname.startsWith("/quiz")

  // Même clé de cache que CataloguePage ("epreuves-inedites-recente") : un visiteur
  // qui atterrit sur le catalogue puis navigue ailleurs ne repaie pas cette requête
  // dans la fenêtre de staleTime (60 s, voir main.tsx). Sert uniquement à savoir s'il
  // existe au moins une inédite pour ce pays - jamais le contenu de la réponse.
  const { data: inediteRecenteData } = useQuery({
    queryKey: ["epreuves-inedites-recente", country, langueCourante()],
    queryFn: ({ signal }) => listEpreuves({ country, origine: "INEDITE", ordering: "recent", langue: langueCourante() }, signal),
    enabled: Boolean(country),
  })
  const hasInedites = Boolean(inediteRecenteData && inediteRecenteData.count > 0)
  // Le point or signale une NOUVEAUTÉ : il s'éteint dès que la personne a regardé les
  // inédites (leur liste ou l'une d'elles) et se rallume si une plus récente est publiée.
  const derniereIneditId = inediteRecenteData?.results[0]?.id
  const ineditesVues = useIneditesVues()
  const surLesInedites = pathname.includes("/epreuves-inedites/") || new URLSearchParams(search).get("origine") === "INEDITE"
  useEffect(() => {
    if (surLesInedites && derniereIneditId !== undefined) marquerIneditesVues(derniereIneditId)
  }, [surLesInedites, derniereIneditId])
  const nouvellesInedites = hasInedites && ineditesNouvelles(derniereIneditId, ineditesVues)

  /**
   * Deux navigations, pas une.
   *
   * Un VISITEUR arrive par une recherche et vient voir ce qu'il y a : Épreuves,
   * Cours, Prix - c'est aussi la version que les robots indexent, elle ne bouge pas.
   *
   * Un ÉLÈVE qui a déclaré son examen n'est plus là pour explorer un catalogue mais
   * pour avancer : Aujourd'hui (sa séance), Réviser (toute la bibliothèque), Ma
   * progression. Trois entrées, parce que les cinq précédentes décrivaient notre
   * modèle de données (deux types de documents, deux outils, une page commerciale) et
   * pas sa façon de réviser - personne ne se dit "je vais faire un quiz", on se dit
   * "je révise les limites".
   *
   * "Quiz" disparaît du menu : un quiz n'est pas une destination, c'est la fin d'une
   * séance (voir SeanceDuJour) et un bouton sur une page de thème. "Parcours" devient
   * "Ma progression" - on y va pour se rassurer, plus pour démarrer, le plan s'en
   * charge. Leurs deux routes restent servies telles quelles.
   *
   * "Prix" ne s'affiche que pour qui n'a pas encore payé : reproposer en permanence
   * d'acheter ce qu'on possède déjà n'est plus de la navigation.
   */
  const suitUnPlan = isAuthenticated && Boolean(user?.cursus_prepare)
  const navLinks: { to: string; label: string; active: boolean; badge: boolean; menuSeulement?: boolean }[] = suitUnPlan
    ? [
        { to: catalogueHomePath(country), label: t("nav.aujourdhui"), active: isAccueil, badge: false },
        { to: epreuvesListPath(country), label: t("nav.reviser"), active: isReviserSection, badge: nouvellesInedites },
        { to: "/parcours", label: t("nav.progression"), active: isParcoursSection, badge: false },
        ...(user?.a_un_abonnement_actif
          ? []
          : [{ to: "/tarifs", label: t("nav.prix"), active: isTarifsSection, badge: false }]),
      ]
    : [
        // « Accueil » seulement dans le menu mobile : sur grand écran le logo y mène déjà, et l'entrée doublerait la barre.
        // Un visiteur arrivé par un lien partagé (un quiz, un corrigé) n'a pas d'autre moyen évident de voir de quoi parle le site.
        { to: catalogueHomePath(country), label: t("nav.accueil"), active: isAccueil, badge: false, menuSeulement: true },
        { to: epreuvesListPath(country), label: t("nav.epreuves"), active: isEpreuvesSection, badge: nouvellesInedites },
        { to: coursListPath(country), label: t("nav.cours"), active: isCoursSection, badge: false },
        // Le quiz d'essai sans compte est ce qui fait goûter le site à un visiteur : pour lui c'est une destination (voir le
        // commentaire ci-dessus, qui ne vaut que pour l'élève qui suit un plan).
        { to: "/quiz", label: t("nav.quiz"), active: pathname.startsWith("/quiz"), badge: false },
        { to: "/tarifs", label: t("nav.prix"), active: isTarifsSection, badge: false },
      ]

  return (
    <header className="sticky top-0 z-40 border-b border-border/80 bg-background/85 backdrop-blur-sm">
      <div className="h-[3px] w-full bg-gradient-to-r from-primary via-gold to-primary" />
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3.5 sm:px-6">
        <div className="flex items-baseline gap-2">
          <Link to={catalogueHomePath(country)} className="group flex items-baseline gap-2">
            <span className="font-display text-xl font-semibold tracking-tight text-primary">
              {SITE_NAME}
            </span>
            {/* La baseline cède la place au compte à rebours dès qu'il y en a un :
                pour un élève qui a déclaré son cursus, "BAC D · J-244" dit la même
                chose que "réussis ton examen", mais avec sa date à lui. Deux textes
                gris côte à côte ne feraient que se diluer. */}
            {!aUnCompteARebours && (
              <span className="hidden whitespace-nowrap font-display text-xs italic text-muted-foreground sm:inline">
                {t("site.baseline")}
              </span>
            )}
          </Link>
          <CompteAReboursBadge variant="pilule" className="hidden whitespace-nowrap sm:inline" />
        </div>
        <div className="flex items-center gap-2">
          {/* Toujours visible (pas de hidden sm:), contrairement aux liens de nav
              desktop plus bas - ce lien rend la recherche accessible depuis
              n'importe quelle page, y compris sur mobile où la place au clavier
              manque le plus. Mène à la page de recherche (thèmes, cours, épreuves,
              exercices, quiz - voir RecherchePage) avec le champ prêt à écrire ; aussi
              atteignable au clavier par « / » et Ctrl/⌘+K. */}
          <Button asChild variant="ghost" size="icon" aria-label={t("nav.rechercher")}>
            <Link to={recherchePath(country)} state={ETAT_FOCUS_RECHERCHE} aria-keyshortcuts="/ Control+K Meta+K">
              <Search className="size-4.5" />
            </Link>
          </Button>
          {/* Le centre d'aide (components/guides/CentreAide) : atteignable de toute page, pour tous. */}
          <Button variant="ghost" size="icon" aria-label={t("guide.aide.ouvrir_label")} onClick={ouvrirCentre}>
            <CircleHelp className="size-4.5" />
          </Button>
          <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="lg:hidden" aria-label={t("nav.ouvrir_menu")}>
                <Menu className="size-5" />
              </Button>
            </SheetTrigger>
            <SheetContent>
              <SheetTitle>{t("nav.menu")}</SheetTitle>
              <SheetDescription>{t("nav.menu_description", { site: SITE_NAME })}</SheetDescription>
              {/* Même raison que le pays et le thème plus bas : retiré de la barre
                  sous `sm` faute de place, jamais retiré du mobile. */}
              <CompteAReboursBadge className="mt-3 block sm:hidden" />
              <nav aria-label={t("nav.menu")} className="mt-3 flex flex-col gap-1">
                {navLinks.map((link) => (
                  <Link
                    key={link.to}
                    to={link.to}
                    onClick={() => setMobileNavOpen(false)}
                    className={
                      link.active
                        ? "flex items-center gap-2 rounded-md bg-secondary px-3 py-2.5 text-base font-medium text-secondary-foreground"
                        : "flex items-center gap-2 rounded-md px-3 py-2.5 text-base font-medium text-foreground hover:bg-accent"
                    }
                  >
                    {link.label}
                    {/* Même point discret que la barre desktop (voir plus bas) - pas de
                        deuxième traitement visuel à maintenir en parallèle. */}
                    {link.badge && (
                      <>
                        <span className="size-1.5 shrink-0 rounded-full bg-gold" aria-hidden="true" />
                        <span className="sr-only"> - {t("nav.nouvelles_inedites")}</span>
                      </>
                    )}
                  </Link>
                ))}
              </nav>
              {/* Pays et thème, retirés de la barre sous `sm` faute de place (voir
                  le commentaire sur leur conteneur `hidden sm:flex`) - ils restent à
                  une tape d'ici, jamais supprimés du mobile. */}
              <div className="mt-4 flex flex-col gap-3 border-t border-border pt-4 sm:hidden">
                <SelecteurLangue className="self-start" />
                <div className="flex items-center justify-between gap-3">
                  <CountrySwitcher dansLeMenu onNavigate={() => setMobileNavOpen(false)} />
                  <ThemeToggle />
                </div>
              </div>
            </SheetContent>
          </Sheet>
          {/* Rendus depuis `navLinks`, comme le menu mobile : les deux listes étaient
              écrites deux fois côte à côte, et un lien ajouté d'un seul côté suffisait
              à les faire diverger silencieusement. Le point or des inédites reste
              porté par l'entrée qui les contient, sans consommer de largeur. */}
          {navLinks.filter((link) => !link.menuSeulement).map((link) => (
            <span key={link.to} className="relative hidden lg:inline-flex">
              <Button asChild variant={link.active ? "secondary" : "ghost"} size="sm">
                <Link to={link.to} title={link.badge ? t("nav.nouvelles_inedites") : undefined}>
                  {link.label}
                  {link.badge && <span className="sr-only"> - {t("nav.nouvelles_inedites")}</span>}
                </Link>
              </Button>
              {link.badge && (
                <span className="pointer-events-none absolute -top-0.5 -right-0.5 flex size-2.5">
                  <span className="absolute inline-flex size-full animate-ping rounded-full bg-gold opacity-75" />
                  <span className="relative inline-flex size-2.5 rounded-full bg-gold ring-2 ring-background" />
                </span>
              )}
            </span>
          ))}
          {/* Sous `sm`, ces deux contrôles secondaires descendent dans le menu (voir
              SheetContent plus haut) : à 375 px la barre réclamait ~419 px pour
              375 disponibles (logo + recherche + menu + pays + thème + connexion),
              et c'est le pays et le thème qu'on consulte le moins souvent. Le
              basculement est à `sm` et non à `lg` : entre les deux, les liens de nav
              desktop sont encore repliés dans le menu, la place ne manque pas. */}
          <div className="hidden items-center gap-2 sm:flex">
            <SelecteurLangue />
            <CountrySwitcher />
            <ThemeToggle />
          </div>
          {authLoading ? (
            // Le token d'accès ne survit jamais à un rechargement de page (voir
            // AuthContext) - une session valide se reconfirme silencieusement en
            // arrière-plan à chaque montage, ce qui prend un aller-retour réseau.
            // Sans ce repli neutre, un utilisateur connecté verrait le bouton
            // "Connexion" s'afficher brièvement à chaque F5, comme s'il avait été
            // déconnecté.
            <Skeleton className="h-8 w-20 rounded-md" />
          ) : isAuthenticated ? (
            <AccountMenu />
          ) : (
            <Button asChild size="sm">
              <Link to="/connexion">{t("nav.connexion")}</Link>
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
