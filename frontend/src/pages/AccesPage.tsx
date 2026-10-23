import { useCallback, useEffect, useState, type FormEvent } from "react"
import { Link, useLocation, useNavigate } from "react-router-dom"
import { AideContextuelle, BoutonAide } from "@/components/guides/AideContextuelle"
import { toast } from "sonner"
import { ArrowRight, BookOpen, CalendarClock, Check, ChevronDown, Loader2, Lock, Pencil, Plus, ShieldCheck, Sparkles, UserPlus } from "lucide-react"

import {
  createProfil,
  listMyInscriptionsInedites,
  listMyInscriptionsIneditesFamille,
  listMyInscriptionsRepetiteur,
  listMyInscriptionsRepetiteurFamille,
  listMySubscriptions,
  listMySubscriptionsFamille,
  listProfils,
  renameProfil,
} from "@/api/endpoints"
import { ApiError, modeParentActif } from "@/api/client"
import type { InscriptionInedite, InscriptionRepetiteur, Profil, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { ChoixMatieres } from "@/components/ChoixMatieres"
import { EnteteCompte, EtatVide, Section } from "@/components/CompteSection"
import { ErreurChargement } from "@/components/ErreurChargement"
import { SecuriteProfils } from "@/components/SecuriteProfils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { estGce } from "@/lib/cursus"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"
import { langueCourante, localeCourante, t, useI18n } from "@/lib/i18n"

// En dessous, la fin de l'abonnement se voit : la jauge passe à l'orange et "Prolonger" devient
// l'action principale de la ligne. Assez tôt pour renouveler sans coupure, assez tard pour ne pas
// harceler quelqu'un qui vient de payer.
const JOURS_AVANT_RENOUVELLEMENT = 14

function joursRestants(expiresAt: string): number {
  return Math.ceil((new Date(expiresAt).getTime() - Date.now()) / 86_400_000)
}

function dateFr(iso: string): string {
  return new Date(iso).toLocaleDateString(localeCourante(), { day: "numeric", month: "long", year: "numeric" })
}

function libelleCursus(cursus: Subscription["cursus"]): string {
  return `${cursus.examen_display}${cursus.series ? ` - ${t("prix.serie", { code: cursus.series.code })}` : ""}`
}

/**
 * Un accès (abonnement ou add-on) : ce qu'il donne, jusqu'à quand, et - surtout - ce qu'il faut faire.
 * Les jours restants se lisent d'un coup d'œil et "Prolonger" apparaît AVANT l'expiration : renouveler
 * quand on est encore en pleine révision, pas après avoir perdu l'accès. Une prolongation repart de
 * l'échéance existante (voir Subscription.extend) : rien n'est perdu à le faire tôt.
 */
function LigneAcces({
  titre, sous_titre, expiresAt, actif, cursusId, profilId, renouvelable = true, inclutInedit = false, gce = false,
}: {
  titre: string
  sous_titre?: string
  expiresAt: string
  actif: boolean
  cursusId: number
  profilId: number
  renouvelable?: boolean
  inclutInedit?: boolean
  /** Examen du GCE : l'élève y choisit ses matières (voir ChoixMatieres). */
  gce?: boolean
}) {
  const [matieresOuvertes, setMatieresOuvertes] = useState(false)
  const jours = joursRestants(expiresAt)
  const bientot = actif && jours <= JOURS_AVANT_RENOUVELLEMENT
  return (
    <li className="rounded-xl border border-border bg-background/60 p-3.5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-semibold leading-snug">{titre}</p>
          {sous_titre && <p className="text-xs text-muted-foreground">{sous_titre}</p>}
          {inclutInedit && (
            <p className="mt-0.5 flex items-center gap-1 text-xs font-medium text-gold-text">
              <Sparkles className="size-3" />
              {t("ac.inedites_incluses")}
            </p>
          )}
        </div>
        {actif ? (
          <Badge variant="success" className="shrink-0 gap-1">
            <Check className="size-3" strokeWidth={3} />
            {t("ac.actif")}
          </Badge>
        ) : (
          <Badge variant="outline" className="shrink-0">{t("ac.expire")}</Badge>
        )}
      </div>

      {actif ? (
        <div className="mt-2 flex flex-wrap items-center justify-between gap-x-3 gap-y-0.5 text-xs">
          <span className={cn("inline-flex items-center gap-1.5 whitespace-nowrap", bientot ? "font-medium text-warning-foreground dark:text-warning" : "text-muted-foreground")}>
            <CalendarClock className="size-3.5" aria-hidden="true" />
            {jours > 1 ? t("ac.jours_restants", { n: jours }) : jours === 1 ? t("ac.dernier_jour") : t("ac.expire_aujourdhui")}
          </span>
          <span className="text-muted-foreground">{t("ac.jusqua", { date: dateFr(expiresAt) })}</span>
        </div>
      ) : (
        <p className="mt-2 text-xs text-muted-foreground">{t("ac.expire_le", { date: dateFr(expiresAt) })}</p>
      )}

      {renouvelable && (!actif || bientot) && (
        <Button asChild size="sm" variant={actif ? "default" : "outline"} className="mt-3 h-11 rounded-full text-xs sm:h-8">
          {/* `profil=` : sans lui, prolonger depuis la carte d'un enfant précis
              retomberait sur le profil par défaut du compte (voir
              payments.views._resoudre_profil), pas nécessairement le bon enfant. */}
          <Link to={`/abonnement?cursus=${cursusId}&profil=${profilId}`}>
            {actif ? t("ac.prolonger") : t("ac.reabonner")}
            <ArrowRight className="size-3.5" />
          </Link>
        </Button>
      )}

      {/* Au GCE, aucune série ne fixe le programme : le choix (et la correction) des matières de CE profil se fait
          ici, sur sa ligne, quel que soit le profil actif - pas seulement depuis la page du compte. */}
      {gce && actif && (
        <div className="mt-3 border-t border-border pt-3">
          <button
            type="button"
            aria-expanded={matieresOuvertes}
            onClick={() => setMatieresOuvertes((o) => !o)}
            className="inline-flex min-h-9 items-center gap-2 text-sm font-medium text-primary hover:underline"
          >
            <BookOpen className="size-4" aria-hidden="true" />
            {t("matieres.titre")}
            <ChevronDown className={cn("size-4 transition-transform", matieresOuvertes && "rotate-180")} aria-hidden="true" />
          </button>
          {matieresOuvertes && (
            <div className="mt-3">
              <ChoixMatieres cible={{ profilId, cursusId }} />
            </div>
          )}
        </div>
      )}
    </li>
  )
}

/**
 * Le prénom d'un profil, renommable en ligne (clic -> champ -> Entrée/blur pour
 * enregistrer). Jamais un modal : c'est un simple libellé, pas une action qui
 * mérite d'interrompre la page.
 */
function NomProfilEditable({ profil, onRenamed }: { profil: Profil; onRenamed: (profil: Profil) => void }) {
  const [editing, setEditing] = useState(false)
  const [valeur, setValeur] = useState(profil.prenom)
  const [saving, setSaving] = useState(false)

  async function enregistrer() {
    const prenom = valeur.trim()
    if (!prenom || prenom === profil.prenom) {
      setValeur(profil.prenom)
      setEditing(false)
      return
    }
    setSaving(true)
    try {
      const updated = await renameProfil(profil.id, prenom)
      onRenamed(updated)
    } catch (err) {
      setValeur(profil.prenom)
      // Sans message, le prénom reprenait simplement son ancienne valeur : on croyait avoir renommé.
      toast.error(err instanceof ApiError ? err.message : t("ac.renommer_erreur"))
    } finally {
      setSaving(false)
      setEditing(false)
    }
  }

  if (editing) {
    return (
      <form
        onSubmit={(e) => {
          e.preventDefault()
          enregistrer()
        }}
        className="flex items-center gap-1.5"
      >
        <Input
          autoFocus
          value={valeur}
          onChange={(e) => setValeur(e.target.value)}
          onBlur={enregistrer}
          disabled={saving}
          maxLength={60}
          className="h-10 w-40 text-sm font-semibold sm:h-8"
        />
        {saving && <Loader2 className="size-4 shrink-0 animate-spin text-muted-foreground" />}
      </form>
    )
  }

  return (
    <button
      type="button"
      onClick={() => setEditing(true)}
      aria-label={t("ac.renommer_aria", { nom: profil.prenom || t("ac.sans_nom_min") })}
      className="group flex min-h-11 items-center gap-1.5 text-left"
    >
      <h3 className="font-display text-base font-semibold">
        {profil.prenom || t("ac.sans_nom")}
      </h3>
      {/* Visible en permanence : sur tactile il n'y a pas de survol qui révèle le crayon, la
          possibilité de renommer restait invisible. Discret au repos, renforcé au survol. */}
      <Pencil className="size-3.5 shrink-0 text-muted-foreground/70 transition-colors group-hover:text-foreground" aria-hidden="true" />
    </button>
  )
}

/** "Ajouter un enfant" : crée le profil puis envoie choisir un cursus à lui payer. */
function AjouterEnfant({ onCreated }: { onCreated: (profil: Profil) => void }) {
  const navigate = useNavigate()
  const [ouvert, setOuvert] = useState(false)
  const [prenom, setPrenom] = useState("")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!prenom.trim()) return
    setSaving(true)
    setError(null)
    try {
      const profil = await createProfil(prenom.trim())
      onCreated(profil)
      navigate(`/tarifs?profil=${profil.id}`)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t("ac.creer_erreur"))
      setSaving(false)
    }
  }

  if (!ouvert) {
    return (
      <button
        type="button"
        onClick={() => setOuvert(true)}
        className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-border px-4 py-3.5 text-sm font-medium text-muted-foreground transition-colors hover:border-primary/40 hover:text-primary"
      >
        <UserPlus className="size-4" />
        {t("ac.ajouter_enfant")}
      </button>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 rounded-xl border border-dashed border-primary/40 bg-primary/[0.03] p-3.5">
      <label htmlFor="nouveau-prenom" className="text-xs font-medium text-muted-foreground">
        {t("ac.prenom_enfant")}
      </label>
      <div className="flex items-center gap-2">
        <Input
          id="nouveau-prenom"
          autoFocus
          value={prenom}
          onChange={(e) => setPrenom(e.target.value)}
          placeholder="Awa"
          maxLength={60}
          disabled={saving}
          className="h-9"
        />
        <Button type="submit" size="sm" disabled={saving || !prenom.trim()} className="h-9 shrink-0 rounded-full">
          {saving ? <Loader2 className="size-4 animate-spin" /> : <Plus className="size-4" />}
          {t("bs.continuer")}
        </Button>
      </div>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </form>
  )
}

export function AccesPage() {
  useI18n()
  useSeo({ title: t("compte.mes_acces") })

  const { isAuthenticated, isLoading, user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  // null = pas encore chargé : un tableau vide initial se lisait « aucun abonnement », donc
  // « Aucun accès actif » s'affichait à tort tant que la réponse n'était pas arrivée (ou échouait).
  const [subscriptions, setSubscriptions] = useState<Subscription[] | null>(null)
  const [inscriptionsInedites, setInscriptionsInedites] = useState<InscriptionInedite[] | null>(null)
  const [inscriptionsRepetiteur, setInscriptionsRepetiteur] = useState<InscriptionRepetiteur[] | null>(null)
  const [profils, setProfils] = useState<Profil[] | null>(null)
  const [erreur, setErreur] = useState(false)
  // Vrai une fois la famille entière chargée en mode parent. Sinon, avec un code parent, le serveur ne rend que le profil
  // actif : un enfant ne lit pas les abonnements de ses frères (users.parent.portee_famille).
  const [famille, setFamille] = useState(false)
  const [chargementFamille, setChargementFamille] = useState(false)

  // Les quatre appels sont indissociables : sans l'un d'eux, l'écran afficherait un état faux
  // (accès manquant, profils absents). Un seul échec suffit donc à basculer sur l'erreur.
  const charger = useCallback(() => {
    setErreur(false)
    setSubscriptions(null)
    setInscriptionsInedites(null)
    setInscriptionsRepetiteur(null)
    setProfils(null)
    setFamille(false)
    const echec = () => setErreur(true)
    listMySubscriptions().then(setSubscriptions).catch(echec)
    listMyInscriptionsInedites().then(setInscriptionsInedites).catch(echec)
    listMyInscriptionsRepetiteur().then(setInscriptionsRepetiteur).catch(echec)
    listProfils().then(setProfils).catch(echec)
  }, [])

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/mes-acces" } })
      return
    }
    charger()
  }, [isLoading, isAuthenticated, navigate, charger])

  // Ancre « #securite » (rappel de « Qui étudie ? ») : la section n'existe qu'une fois les profils chargés.
  const securitePrete = profils !== null
  useEffect(() => {
    if (location.hash !== "#securite" || !securitePrete) return
    document.getElementById("securite")?.scrollIntoView({ block: "start" })
  }, [location.hash, securitePrete])

  // Le premier appel demande le code parent s'il manque (le client rejoue ensuite la requête) ; les deux autres partent
  // une fois le mode parent ouvert, pour ne jamais afficher trois fois la même saisie.
  async function voirFamille() {
    setChargementFamille(true)
    try {
      const abonnements = await listMySubscriptionsFamille()
      const [inedites, repetiteur] = await Promise.all([
        listMyInscriptionsIneditesFamille(),
        listMyInscriptionsRepetiteurFamille(),
      ])
      setSubscriptions(abonnements)
      setInscriptionsInedites(inedites)
      setInscriptionsRepetiteur(repetiteur)
      setFamille(true)
    } catch (err) {
      // Refuser de saisir le code est un choix, pas une panne.
      if (!(err instanceof ApiError && err.status === 403)) toast.error(t("ac.famille_erreur"))
    } finally {
      setChargementFamille(false)
    }
  }

  if (isLoading) return null

  const charge =
    subscriptions !== null && inscriptionsInedites !== null && inscriptionsRepetiteur !== null && profils !== null

  // L'add-on Épreuves Inédites n'est plus achetable séparément (retiré le 2026-09-30) :
  // il est désormais TOUJOURS activé pour la même durée que l'abonnement qui l'inclut
  // (voir payments.models._activer_acces, Plan.inclut_inedit). Une ligne séparée avec
  // sa propre échéance ne ferait donc que dupliquer celle de l'abonnement - inutile et
  // source de confusion ("deux abonnements actifs ?"). On s'en sert seulement pour
  // savoir SUR QUEL cursus l'afficher comme un simple badge sur la ligne d'abonnement.
  // Rapproché par (profil, cursus) : dans une famille, un enfant ne doit pas hériter du badge d'un autre.
  const cursusAvecInedit = new Set(
    (inscriptionsInedites ?? []).filter((i) => i.is_active).map((i) => `${i.profil.id}-${i.cursus.id}`),
  )

  // Les deux sources d'accès restantes (abonnement, add-on répétiteur) partagent la même
  // forme (cursus/expires_at/is_active) : une seule liste plutôt que deux blocs distincts qui
  // répètent chacun leur propre état vide.
  const acces = [
    ...(subscriptions ?? []).map((sub) => ({
      key: `sub-${sub.id}`,
      titre: libelleCursus(sub.cursus),
      // Le nom du plan vient du serveur, en français : hors français, la formule unique est traduite
      // (même règle que SubscribePage.nomPlan).
      sous_titre:
        sub.duration_mode === "JUSQUA_EXAMEN" && langueCourante() !== "fr"
          ? t("prix.formule")
          : sub.plan_name ?? (sub.duration_mode === "JUSQUA_EXAMEN" ? t("prix.formule") : t("ac.mensuel")),
      expiresAt: sub.expires_at,
      actif: sub.is_active,
      cursusId: sub.cursus.id,
      profilId: sub.profil.id,
      // Un accès "Jusqu'à l'Examen" couvre déjà l'échéance : lui proposer de prolonger n'aurait
      // aucun sens tant qu'il est actif.
      renouvelable: sub.duration_mode !== "JUSQUA_EXAMEN" || !sub.is_active,
      inclutInedit: cursusAvecInedit.has(`${sub.profil.id}-${sub.cursus.id}`),
      gce: estGce(sub.cursus),
    })),
    ...(inscriptionsRepetiteur ?? []).map((i) => ({
      key: `repet-${i.id}`,
      titre: libelleCursus(i.cursus),
      sous_titre: t("ac.addon_fiches"),
      expiresAt: i.expires_at,
      actif: i.is_active,
      cursusId: i.cursus.id,
      profilId: i.profil.id,
      renouvelable: true,
    })),
  ]

  // Un groupe par profil (enfant), dans l'ordre où ils ont été ajoutés (voir
  // Profil.ordre) - même un compte à un seul profil en voit un, personnalisable :
  // c'est exactement ce que "nommer chaque abonnement" demande, pas seulement les
  // comptes à plusieurs enfants.
  // Portée limitée au profil actif (code parent défini hors mode parent, ou session enfant) : les autres enfants n'ont pas
  // été chargés, leur groupe afficherait à tort « Choisir un abonnement ».
  const porteeLimitee =
    !famille && (!!user?.session_restreinte || (!!user?.pin_parent_actif && !modeParentActif())) && (profils?.length ?? 0) > 1
  // Verrouillé : un code parent protège le compte et le mode parent est fermé. Seuls les accès du profil actif se voient ;
  // les autres enfants, la sécurité des profils et l'ajout d'enfant attendent le code (test élève Gogo, C-F3).
  const verrouille = porteeLimitee && !user?.session_restreinte
  const groupes = (profils ?? [])
    .filter((profil) => !porteeLimitee || profil.id === user?.profil_actif?.id)
    .map((profil) => ({
      profil,
      acces: acces.filter((a) => a.profilId === profil.id),
    }))

  function renommer(profilRenomme: Profil) {
    setProfils((prev) => (prev ?? []).map((p) => (p.id === profilRenomme.id ? profilRenomme : p)))
  }

  function ajouterProfil(nouveau: Profil) {
    setProfils((prev) => [...(prev ?? []), nouveau])
  }

  return (
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:py-10 sm:px-6">
      <EnteteCompte
        icone={Sparkles}
        titre={t("compte.mes_acces")}
        sousTitre={t("ac.sous_titre")}
      />

      <div className="mb-4">
        <BoutonAide guide="examen-matieres" className="-ml-2.5" />
        <AideContextuelle guide="examen-matieres" className="mt-1" />
      </div>

      <Section icone={Sparkles} titre={t("ac.section")}>
        {verrouille && charge && !erreur && (
          <div className="mb-4 flex flex-col gap-2 rounded-lg border border-border bg-muted/30 p-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-muted-foreground">
              {t("ac.portee_limitee", { prenom: user?.profil_actif?.prenom || t("compte.profil_sans_nom") })}
            </p>
            <Button size="sm" variant="outline" className="h-11 sm:h-8" disabled={chargementFamille} onClick={voirFamille}>
              {chargementFamille ? <Loader2 className="size-4 animate-spin" /> : <Lock className="size-4" />}
              {t("ac.voir_famille")}
            </Button>
          </div>
        )}
        {erreur ? (
          // Une panne n'est pas « aucun accès » : l'élève qui a payé doit voir qu'on n'a pas pu
          // lire son compte, pas qu'il n'a rien.
          <ErreurChargement compact objet={t("ac.objet")} onRetry={charger} />
        ) : !charge ? (
          <p className="text-sm text-muted-foreground">{t("matieres.chargement")}</p>
        ) : acces.length === 0 ? (
          <EtatVide
            texte={t("ac.aucun_acces")}
            lien="/tarifs"
            libelleLien={t("ar.formules")}
          />
        ) : (
          <div className="flex flex-col gap-5">
            {groupes.map(({ profil, acces: accesDuProfil }) => (
              <div key={profil.id} className="flex flex-col gap-2.5">
                <NomProfilEditable profil={profil} onRenamed={renommer} />
                {accesDuProfil.length > 0 ? (
                  <ul className="flex flex-col gap-2.5">
                    {accesDuProfil.map(({ key, ...props }) => <LigneAcces key={key} {...props} />)}
                  </ul>
                ) : (
                  <Button asChild size="sm" variant="outline" className="h-11 w-fit rounded-full text-xs sm:h-8">
                    <Link to={`/tarifs?profil=${profil.id}`}>
                      {t("ac.choisir_abonnement")}
                      <ArrowRight className="size-3.5" />
                    </Link>
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}

        {charge && !user?.session_restreinte && !verrouille && (
          <div className="mt-5">
            <AjouterEnfant onCreated={ajouterProfil} />
          </div>
        )}
      </Section>

      {charge && profils && !user?.session_restreinte && !verrouille && (
        <Section icone={ShieldCheck} titre={t("ac.securite")} id="securite">
          <SecuriteProfils
            profils={profils}
            onProfilChange={(maj) => setProfils((prev) => (prev ?? []).map((p) => (p.id === maj.id ? maj : p)))}
          />
        </Section>
      )}
    </div>
  )
}
