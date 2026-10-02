import { useEffect, useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"
import { ArrowRight, CalendarClock, Check, Loader2, Pencil, Plus, ShieldCheck, Sparkles, UserPlus } from "lucide-react"

import {
  createProfil,
  listMyInscriptionsInedites,
  listMyInscriptionsRepetiteur,
  listMySubscriptions,
  listProfils,
  renameProfil,
} from "@/api/endpoints"
import { ApiError } from "@/api/client"
import type { InscriptionInedite, InscriptionRepetiteur, Profil, Subscription } from "@/api/types"
import { useAuth } from "@/context/AuthContext"
import { EnteteCompte, EtatVide, Section } from "@/components/CompteSection"
import { SecuriteProfils } from "@/components/SecuriteProfils"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useSeo } from "@/lib/seo"
import { cn } from "@/lib/utils"

// En dessous, la fin de l'abonnement se voit : la jauge passe à l'orange et "Prolonger" devient
// l'action principale de la ligne. Assez tôt pour renouveler sans coupure, assez tard pour ne pas
// harceler quelqu'un qui vient de payer.
const JOURS_AVANT_RENOUVELLEMENT = 14

function joursRestants(expiresAt: string): number {
  return Math.ceil((new Date(expiresAt).getTime() - Date.now()) / 86_400_000)
}

function dateFr(iso: string): string {
  return new Date(iso).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric" })
}

function libelleCursus(cursus: Subscription["cursus"]): string {
  return `${cursus.examen_display}${cursus.series ? ` - Série ${cursus.series.code}` : ""}`
}

/**
 * Un accès (abonnement ou add-on) : ce qu'il donne, jusqu'à quand, et - surtout - ce qu'il faut faire.
 * Les jours restants se lisent d'un coup d'œil et "Prolonger" apparaît AVANT l'expiration : renouveler
 * quand on est encore en pleine révision, pas après avoir perdu l'accès. Une prolongation repart de
 * l'échéance existante (voir Subscription.extend) : rien n'est perdu à le faire tôt.
 */
function LigneAcces({
  titre, sous_titre, expiresAt, actif, cursusId, profilId, renouvelable = true, inclutInedit = false,
}: {
  titre: string
  sous_titre?: string
  expiresAt: string
  actif: boolean
  cursusId: number
  profilId: number
  renouvelable?: boolean
  inclutInedit?: boolean
}) {
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
              Épreuves inédites incluses
            </p>
          )}
        </div>
        {actif ? (
          <Badge variant="success" className="shrink-0 gap-1">
            <Check className="size-3" strokeWidth={3} />
            Actif
          </Badge>
        ) : (
          <Badge variant="outline" className="shrink-0">Expiré</Badge>
        )}
      </div>

      {actif ? (
        <div className="mt-2 flex flex-wrap items-center justify-between gap-x-3 gap-y-0.5 text-xs">
          <span className={cn("inline-flex items-center gap-1.5 whitespace-nowrap", bientot ? "font-medium text-warning-foreground dark:text-warning" : "text-muted-foreground")}>
            <CalendarClock className="size-3.5" aria-hidden="true" />
            {jours > 1 ? `${jours} jours restants` : jours === 1 ? "Dernier jour" : "Expire aujourd'hui"}
          </span>
          <span className="text-muted-foreground">jusqu'au {dateFr(expiresAt)}</span>
        </div>
      ) : (
        <p className="mt-2 text-xs text-muted-foreground">Expiré le {dateFr(expiresAt)}.</p>
      )}

      {renouvelable && (!actif || bientot) && (
        <Button asChild size="sm" variant={actif ? "default" : "outline"} className="mt-3 h-8 rounded-full text-xs">
          {/* `profil=` : sans lui, prolonger depuis la carte d'un enfant précis
              retomberait sur le profil par défaut du compte (voir
              payments.views._resoudre_profil), pas nécessairement le bon enfant. */}
          <Link to={`/abonnement?cursus=${cursusId}&profil=${profilId}`}>
            {actif ? "Prolonger" : "Se réabonner"}
            <ArrowRight className="size-3.5" />
          </Link>
        </Button>
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
    } catch {
      setValeur(profil.prenom)
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
          className="h-8 w-40 text-sm font-semibold"
        />
        {saving && <Loader2 className="size-4 shrink-0 animate-spin text-muted-foreground" />}
      </form>
    )
  }

  return (
    <button
      type="button"
      onClick={() => setEditing(true)}
      className="group flex items-center gap-1.5 text-left"
    >
      <h3 className="font-display text-base font-semibold">
        {profil.prenom || "Sans nom"}
      </h3>
      <Pencil className="size-3.5 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
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
      setError(err instanceof ApiError ? err.message : "Impossible de créer ce profil.")
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
        Ajouter un enfant
      </button>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 rounded-xl border border-dashed border-primary/40 bg-primary/[0.03] p-3.5">
      <label htmlFor="nouveau-prenom" className="text-xs font-medium text-muted-foreground">
        Prénom de l'enfant
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
          Continuer
        </Button>
      </div>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </form>
  )
}

export function AccesPage() {
  useSeo({ title: "Mes accès" })

  const { isAuthenticated, isLoading, user } = useAuth()
  const navigate = useNavigate()
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [inscriptionsInedites, setInscriptionsInedites] = useState<InscriptionInedite[] | null>(null)
  const [inscriptionsRepetiteur, setInscriptionsRepetiteur] = useState<InscriptionRepetiteur[] | null>(null)
  const [profils, setProfils] = useState<Profil[] | null>(null)

  useEffect(() => {
    if (isLoading) return
    if (!isAuthenticated) {
      navigate("/connexion", { state: { from: "/mes-acces" } })
      return
    }
    listMySubscriptions().then(setSubscriptions)
    listMyInscriptionsInedites().then(setInscriptionsInedites)
    listMyInscriptionsRepetiteur().then(setInscriptionsRepetiteur)
    listProfils().then(setProfils)
  }, [isLoading, isAuthenticated, navigate])

  if (isLoading) return null

  const charge = inscriptionsInedites !== null && inscriptionsRepetiteur !== null && profils !== null

  // L'add-on Épreuves Inédites n'est plus achetable séparément (retiré le 2026-09-30) :
  // il est désormais TOUJOURS activé pour la même durée que l'abonnement qui l'inclut
  // (voir payments.models._activer_acces, Plan.inclut_inedit). Une ligne séparée avec
  // sa propre échéance ne ferait donc que dupliquer celle de l'abonnement - inutile et
  // source de confusion ("deux abonnements actifs ?"). On s'en sert seulement pour
  // savoir SUR QUEL cursus l'afficher comme un simple badge sur la ligne d'abonnement.
  const cursusAvecInedit = new Set(
    (inscriptionsInedites ?? []).filter((i) => i.is_active).map((i) => i.cursus.id),
  )

  // Les deux sources d'accès restantes (abonnement, add-on répétiteur) partagent la même
  // forme (cursus/expires_at/is_active) : une seule liste plutôt que deux blocs distincts qui
  // répètent chacun leur propre état vide.
  const acces = [
    ...subscriptions.map((sub) => ({
      key: `sub-${sub.id}`,
      titre: libelleCursus(sub.cursus),
      sous_titre: sub.plan_name ?? (sub.duration_mode === "JUSQUA_EXAMEN" ? "Jusqu'à l'Examen" : "Mensuel"),
      expiresAt: sub.expires_at,
      actif: sub.is_active,
      cursusId: sub.cursus.id,
      profilId: sub.profil.id,
      // Un accès "Jusqu'à l'Examen" couvre déjà l'échéance : lui proposer de prolonger n'aurait
      // aucun sens tant qu'il est actif.
      renouvelable: sub.duration_mode !== "JUSQUA_EXAMEN" || !sub.is_active,
      inclutInedit: cursusAvecInedit.has(sub.cursus.id),
    })),
    ...(inscriptionsRepetiteur ?? []).map((i) => ({
      key: `repet-${i.id}`,
      titre: libelleCursus(i.cursus),
      sous_titre: "Add-on Fiches",
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
  const groupes = (profils ?? []).map((profil) => ({
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
        titre="Mes accès"
        sousTitre="Ce que ton compte débloque aujourd'hui, examen par examen."
      />

      <Section icone={Sparkles} titre="Abonnements et accès">
        {!charge ? (
          <p className="text-sm text-muted-foreground">Chargement…</p>
        ) : acces.length === 0 ? (
          <EtatVide
            texte="Aucun accès actif pour le moment. Choisis ton examen pour débloquer les corrigés, les cours et ta séance du jour."
            lien="/tarifs"
            libelleLien="Voir les formules"
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
                  <Button asChild size="sm" variant="outline" className="h-8 w-fit rounded-full text-xs">
                    <Link to={`/tarifs?profil=${profil.id}`}>
                      Choisir un abonnement
                      <ArrowRight className="size-3.5" />
                    </Link>
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}

        {charge && !user?.session_restreinte && (
          <div className="mt-5">
            <AjouterEnfant onCreated={ajouterProfil} />
          </div>
        )}
      </Section>

      {charge && profils && !user?.session_restreinte && (
        <Section icone={ShieldCheck} titre="Sécurité des profils">
          <SecuriteProfils
            profils={profils}
            onProfilChange={(maj) => setProfils((prev) => (prev ?? []).map((p) => (p.id === maj.id ? maj : p)))}
          />
        </Section>
      )}
    </div>
  )
}
