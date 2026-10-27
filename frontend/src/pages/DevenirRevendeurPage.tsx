import { useState, type FormEvent, type ReactNode } from "react"
import { Link } from "react-router-dom"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { ArrowRight, Briefcase, Check, ChevronDown, GraduationCap, Handshake, Loader2, RefreshCw, School } from "lucide-react"

import { ApiError } from "@/api/client"
import {
  envoyerCodeCandidature, getCandidatureRevendeur, putCandidatureRevendeur, retirerCandidature, soumettreCandidature,
  verifierNumeroCandidature,
} from "@/api/endpoints"
import type { CandidatureRevendeur, ChampsCandidature, EtatCandidature, TypeRevendeur } from "@/api/types"
import { CharteRevendeur } from "@/components/CharteRevendeur"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { useAuth } from "@/context/AuthContext"
import { localeCourante, t, useI18n } from "@/lib/i18n"
import { useSeo } from "@/lib/seo"
import { chiffresNumeroLocal } from "@/lib/telephone"
import { cn } from "@/lib/utils"

const TYPES: TypeRevendeur[] = ["COMMERCIAL", "REPETITEUR", "ECOLE_CENTRE"]
const OPERATEURS = [
  { valeur: "ORANGE", libelle: "Orange Money" },
  { valeur: "MTN", libelle: "MTN Mobile Money" },
] as const

const CLE = ["revendeur", "candidature"] as const

/** Un code d'erreur du serveur devient une phrase dans la langue de la page ; sinon le message de l'API (délais d'envoi de code). */
function messageErreur(err: unknown): string {
  if (err instanceof ApiError) {
    switch (err.code) {
      case "champs_manquants": return t("cand.err_champs_manquants")
      case "numero_non_verifie": return t("cand.err_numero_non_verifie")
      case "charte_non_acceptee": return t("cand.err_charte_non_acceptee")
      case "code_invalide": return t("cand.err_code_invalide")
      case "numero_manquant": return t("cand.err_numero_manquant")
      case "non_modifiable": return t("cand.err_non_modifiable")
      case "refus_recent": return t("cand.err_refus_recent")
    }
    return err.message
  }
  return t("cand.err_generique")
}

function dateLongue(iso: string): string {
  return new Date(iso).toLocaleDateString(localeCourante(), { day: "numeric", month: "long", year: "numeric" })
}

export function DevenirRevendeurPage() {
  useI18n()
  useSeo({ title: t("cand.titre"), noindex: true })

  const { isAuthenticated, isLoading } = useAuth()

  const etat = useQuery({
    queryKey: CLE,
    queryFn: ({ signal }) => getCandidatureRevendeur(signal),
    enabled: isAuthenticated,
  })

  if (isLoading) return null

  return (
    // Même largeur que l'en-tête du site (max-w-5xl).
    <div className="mx-auto max-w-5xl animate-fade-up px-4 py-6 sm:px-6 sm:py-10">
      <Hero visiteur={!isAuthenticated} />

      {!isAuthenticated ? (
        // Un visiteur lit d'abord le principe ; la connexion ne vient qu'au moment de candidater.
        <div className="flex flex-col gap-6">
          <Principe horizontal />
          <Types />
        </div>
      ) : etat.isPending ? (
        <div className="flex flex-col gap-3" aria-busy="true" aria-label={t("cand.chargement")}>
          <Skeleton className="h-32 rounded-2xl" />
          <Skeleton className="h-48 rounded-2xl" />
        </div>
      ) : etat.isError ? (
        <div role="alert" className="flex items-center justify-between gap-4 rounded-2xl border border-border bg-card px-5 py-4">
          <p className="text-sm text-muted-foreground">{t("cand.erreur")}</p>
          <Button onClick={() => void etat.refetch()} variant="outline" size="sm" className="shrink-0 rounded-full">
            <RefreshCw className="size-3.5" />
            {t("erreur.reessayer")}
          </Button>
        </div>
      ) : (
        <Contenu etat={etat.data} />
      )}
    </div>
  )
}

function Carte({ titre, children, ton = "neutre" }: { titre: string; children: ReactNode; ton?: "neutre" | "succes" | "attention" }) {
  return (
    <section
      className={cn(
        "rounded-2xl border p-5",
        ton === "succes" && "border-success/40 bg-success/[0.06]",
        ton === "attention" && "border-warning/40 bg-warning/10",
        ton === "neutre" && "border-border bg-card",
      )}
    >
      <h2 className="font-display text-xl font-semibold">{titre}</h2>
      <div className="mt-3 flex flex-col gap-3 text-sm">{children}</div>
    </section>
  )
}

function Contenu({ etat }: { etat: EtatCandidature }) {
  const client = useQueryClient()
  const { candidature } = etat

  if (candidature?.statut === "ACCEPTEE") {
    return (
      <Carte titre={t("cand.acceptee_titre")} ton="succes">
        <p>{t("cand.acceptee_texte", { code: candidature.code })}</p>
        <Button asChild className="w-fit rounded-full">
          <Link to="/espace-revendeur">{t("cand.acceptee_lien")}</Link>
        </Button>
      </Carte>
    )
  }

  if (etat.raison === "deja_revendeur") {
    return (
      <Carte titre={t("cand.deja_revendeur")} ton="succes">
        <Button asChild className="w-fit rounded-full">
          <Link to="/espace-revendeur">{t("cand.acceptee_lien")}</Link>
        </Button>
      </Carte>
    )
  }

  if (candidature?.statut === "SOUMISE") {
    return <EnAttente candidature={candidature} onChange={() => void client.invalidateQueries({ queryKey: CLE })} />
  }

  // Un refus récent : le motif, et la date à partir de laquelle on peut réessayer.
  if (candidature?.statut === "REFUSEE" && !etat.peut_candidater) {
    return (
      <Carte titre={t("cand.refusee_titre")} ton="attention">
        {candidature.motif && <p>{t("cand.motif", { motif: candidature.motif })}</p>}
        {etat.reouverture_le && <p>{t("cand.refusee_reouverture", { date: dateLongue(etat.reouverture_le) })}</p>}
      </Carte>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      {candidature?.statut === "REFUSEE" && (
        <Carte titre={t("cand.refusee_titre")} ton="attention">
          {candidature.motif && <p>{t("cand.motif", { motif: candidature.motif })}</p>}
        </Carte>
      )}
      {candidature?.statut === "A_COMPLETER" && (
        <Carte titre={t("cand.complement_titre")} ton="attention">
          <p>{t("cand.motif", { motif: candidature.motif })}</p>
        </Carte>
      )}
      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_21rem]">
        <Formulaire
          // Une nouvelle candidature après un refus ou un retrait repart de zéro.
          depart={candidature && (candidature.statut === "BROUILLON" || candidature.statut === "A_COMPLETER") ? candidature : null}
          charteVersion={etat.charte_version}
          onChange={() => void client.invalidateQueries({ queryKey: CLE })}
        />
        <div className="order-first lg:sticky lg:top-24 lg:order-last">
          <Principe />
        </div>
      </div>
    </div>
  )
}

/** L'en-tête de la page : promesse, trois chiffres, et la connexion pour un visiteur. */
function Hero({ visiteur }: { visiteur: boolean }) {
  const chiffres = ["1", "2", "3"] as const
  return (
    <header className="relative mb-8 overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/[0.12] via-primary/[0.04] to-gold/[0.12] p-6 sm:p-10">
      <div
        aria-hidden
        className="absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
          backgroundSize: "24px 24px",
        }}
      />
      <div className="relative">
        <p className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-primary">
          <Handshake className="size-3.5" aria-hidden="true" />
          {t("cand.eyebrow")}
        </p>
        <h1 className="mt-4 max-w-2xl font-display text-3xl font-semibold tracking-tight text-balance sm:text-5xl">{t("cand.titre")}</h1>
        <p className="mt-3 max-w-2xl text-base text-muted-foreground sm:text-lg">{t("cand.sous_titre")}</p>

        <dl className="mt-7 grid grid-cols-3 gap-3 sm:max-w-xl">
          {chiffres.map((n) => (
            <div key={n} className="rounded-2xl border border-border/70 bg-card/80 px-3 py-3 backdrop-blur-sm sm:px-4">
              <dd className="font-display text-base font-semibold leading-none text-primary sm:text-2xl">{t(`cand.chiffre_${n}_v`)}</dd>
              <dt className="mt-1.5 text-xs leading-snug text-muted-foreground">{t(`cand.chiffre_${n}_l`)}</dt>
            </div>
          ))}
        </dl>

        {visiteur && (
          <div className="mt-7 flex flex-col gap-2">
            <Button asChild size="lg" className="w-fit rounded-full px-6">
              <Link to="/connexion" state={{ from: "/devenir-revendeur" }}>
                {t("cand.se_connecter")}
                <ArrowRight className="size-4" aria-hidden="true" />
              </Link>
            </Button>
            <p className="max-w-md text-xs text-muted-foreground">{t("cand.se_connecter_aide")}</p>
          </div>
        )}
      </div>
    </header>
  )
}

/** Ce que le candidat doit savoir avant de remplir : le gain, le délai de réponse, et ce qui se passe ensuite. */
function Principe({ horizontal = false }: { horizontal?: boolean }) {
  const etapes = ["cand.principe_1", "cand.principe_2", "cand.principe_3", "cand.principe_4"] as const
  return (
    <section aria-labelledby="cand-principe" className="rounded-2xl border border-border bg-card p-5 sm:p-6">
      <h2 id="cand-principe" className="font-display text-xl font-semibold">{t("cand.principe_titre")}</h2>
      <ol className={cn("mt-4 grid gap-4", horizontal && "sm:grid-cols-2 lg:grid-cols-4")}>
        {etapes.map((cle, i) => (
          <li key={cle} className="flex items-start gap-3 text-sm">
            <span
              aria-hidden="true"
              className="flex size-7 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground"
            >
              {i + 1}
            </span>
            <span className="pt-0.5 leading-relaxed">{t(cle)}</span>
          </li>
        ))}
      </ol>
    </section>
  )
}

/** À qui s'adresse le programme : les trois profils acceptés. */
function Types() {
  const profils = [
    { cle: "commercial", icone: Briefcase },
    { cle: "repetiteur", icone: GraduationCap },
    { cle: "ecole", icone: School },
  ] as const
  return (
    <section aria-labelledby="cand-types">
      <h2 id="cand-types" className="mb-3 font-display text-xl font-semibold">{t("cand.types_titre")}</h2>
      <ul className="grid gap-3 sm:grid-cols-3">
        {profils.map(({ cle, icone: Icone }) => (
          <li key={cle} className="rounded-2xl border border-border bg-card p-5">
            <span className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <Icone className="size-5" aria-hidden="true" />
            </span>
            <p className="mt-3 font-display text-lg font-semibold">{t(`cand.types_${cle}`)}</p>
            <p className="mt-1 text-sm text-muted-foreground">{t(`cand.types_${cle}_texte`)}</p>
          </li>
        ))}
      </ul>
    </section>
  )
}

function EnAttente({ candidature, onChange }: { candidature: CandidatureRevendeur; onChange: () => void }) {
  const [retrait, setRetrait] = useState(false)
  const [erreur, setErreur] = useState<string | null>(null)

  async function retirer() {
    setErreur(null)
    setRetrait(true)
    try {
      await retirerCandidature()
      onChange()
    } catch (err) {
      setErreur(messageErreur(err))
    } finally {
      setRetrait(false)
    }
  }

  return (
    <Carte titre={t("cand.attente_titre")}>
      <p>
        {candidature.nom_affiche} · {t(`rev.type_${candidature.type || "REPETITEUR"}`)}
        {candidature.ville ? ` · ${candidature.ville}` : ""}
      </p>
      <p className="text-muted-foreground">{t("cand.attente_texte")}</p>
      {erreur && <p role="alert" className="text-destructive">{erreur}</p>}
      <Button onClick={() => void retirer()} disabled={retrait} variant="outline" className="w-fit rounded-full">
        {retrait && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
        {t("cand.retirer")}
      </Button>
    </Carte>
  )
}

interface Champs {
  type: TypeRevendeur | ""
  nom_affiche: string
  ville: string
  presentation: string
  etablissement: string
  fonction: string
  operateur_versement: "ORANGE" | "MTN" | ""
  numero_versement: string
}

function champsDe(c: CandidatureRevendeur | null): Champs {
  return {
    type: c?.type ?? "",
    nom_affiche: c?.nom_affiche ?? "",
    ville: c?.ville ?? "",
    presentation: c?.presentation ?? "",
    etablissement: c?.etablissement ?? "",
    fonction: c?.fonction ?? "",
    operateur_versement: c?.operateur_versement ?? "",
    numero_versement: c?.numero_versement ?? "",
  }
}

function Formulaire({ depart, charteVersion, onChange }: { depart: CandidatureRevendeur | null; charteVersion: string; onChange: () => void }) {
  const [champs, setChamps] = useState<Champs>(() => champsDe(depart))
  // Le numéro est « vérifié » tant que celui qu'on voit est celui que le serveur a validé.
  const [verifie, setVerifie] = useState(() => depart?.numero_verifie ?? false)
  const [codeEnvoyeA, setCodeEnvoyeA] = useState<string | null>(null)
  const [code, setCode] = useState("")
  const [charteOuverte, setCharteOuverte] = useState(false)
  const [charteAcceptee, setCharteAcceptee] = useState(false)
  const [occupe, setOccupe] = useState<null | "code" | "verif" | "envoi" | "brouillon">(null)
  const [erreur, setErreur] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)

  function modifier<K extends keyof Champs>(cle: K, valeur: Champs[K]) {
    setChamps((c) => ({ ...c, [cle]: valeur }))
    setInfo(null)
    if (cle === "numero_versement") {
      setVerifie(false)
      setCodeEnvoyeA(null)
    }
  }

  const ecole = champs.type === "ECOLE_CENTRE"
  const numeroValide = /^6\d{8}$/.test(champs.numero_versement)

  /** Envoie le brouillon : le serveur garde ce qui est saisi, et c'est sur lui que portent la vérification et l'envoi. */
  async function enregistrer(): Promise<CandidatureRevendeur> {
    const corps: ChampsCandidature = {
      nom_affiche: champs.nom_affiche, ville: champs.ville, presentation: champs.presentation,
      etablissement: champs.etablissement, fonction: champs.fonction, numero_versement: champs.numero_versement,
      ...(champs.type ? { type: champs.type } : {}),
      ...(champs.operateur_versement ? { operateur_versement: champs.operateur_versement } : {}),
    }
    return putCandidatureRevendeur(corps)
  }

  async function agir(nom: NonNullable<typeof occupe>, action: () => Promise<void>) {
    setErreur(null)
    setInfo(null)
    setOccupe(nom)
    try {
      await action()
    } catch (err) {
      setErreur(messageErreur(err))
    } finally {
      setOccupe(null)
    }
  }

  const brouillon = () => agir("brouillon", async () => {
    await enregistrer()
    setInfo(t("cand.enregistre"))
    onChange()
  })

  const demanderCode = () => agir("code", async () => {
    const enregistree = await enregistrer()
    setVerifie(enregistree.numero_verifie)
    await envoyerCodeCandidature()
    setCodeEnvoyeA(champs.numero_versement)
  })

  const verifier = () => agir("verif", async () => {
    const resultat = await verifierNumeroCandidature(code.trim())
    setVerifie(resultat.numero_verifie)
    setCode("")
  })

  const envoyer = (e: FormEvent) => {
    e.preventDefault()
    void agir("envoi", async () => {
      await enregistrer()
      await soumettreCandidature(charteVersion, charteAcceptee)
      onChange()
    })
  }

  return (
    <form onSubmit={envoyer} className="flex flex-col gap-6" noValidate>
      <Carte titre={t("cand.etape_profil")}>
        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 text-sm font-medium">{t("cand.type_label")}</legend>
          <div className="grid gap-2 sm:grid-cols-3">
            {TYPES.map((type) => (
              <label
                key={type}
                className={cn(
                  "flex cursor-pointer items-center gap-2 rounded-xl border-2 px-3 py-2.5 text-sm font-medium transition-colors",
                  champs.type === type ? "border-primary bg-accent" : "border-input",
                )}
              >
                <input
                  type="radio"
                  name="type-revendeur"
                  className="sr-only"
                  checked={champs.type === type}
                  onChange={() => modifier("type", type)}
                />
                {t(`rev.type_${type}`)}
              </label>
            ))}
          </div>
        </fieldset>

        <Champ id="cand-nom" libelle={t("cand.nom_label")} aide={t("cand.nom_aide")}>
          <Input id="cand-nom" value={champs.nom_affiche} maxLength={150} onChange={(e) => modifier("nom_affiche", e.target.value)} />
        </Champ>
        <Champ id="cand-ville" libelle={t("cand.ville_label")}>
          <Input id="cand-ville" value={champs.ville} maxLength={100} onChange={(e) => modifier("ville", e.target.value)} />
        </Champ>
        {ecole && (
          <>
            <Champ id="cand-etab" libelle={t("cand.etablissement_label")}>
              <Input id="cand-etab" value={champs.etablissement} maxLength={150} onChange={(e) => modifier("etablissement", e.target.value)} />
            </Champ>
            <Champ id="cand-fonction" libelle={t("cand.fonction_label")}>
              <Input id="cand-fonction" value={champs.fonction} maxLength={100} onChange={(e) => modifier("fonction", e.target.value)} />
            </Champ>
          </>
        )}
        <Champ id="cand-presentation" libelle={t("cand.presentation_label")} aide={t("cand.presentation_aide")}>
          <textarea
            id="cand-presentation"
            value={champs.presentation}
            maxLength={1000}
            rows={4}
            onChange={(e) => modifier("presentation", e.target.value)}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring/50"
          />
        </Champ>
      </Carte>

      <Carte titre={t("cand.etape_versement")}>
        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 text-sm font-medium">{t("cand.operateur_label")}</legend>
          <div className="grid gap-2 sm:grid-cols-2">
            {OPERATEURS.map((op) => (
              <label
                key={op.valeur}
                className={cn(
                  "flex cursor-pointer items-center gap-2 rounded-xl border-2 px-3 py-2.5 text-sm font-medium transition-colors",
                  champs.operateur_versement === op.valeur ? "border-primary bg-accent" : "border-input",
                )}
              >
                <input
                  type="radio"
                  name="operateur-revendeur"
                  className="sr-only"
                  checked={champs.operateur_versement === op.valeur}
                  onChange={() => modifier("operateur_versement", op.valeur)}
                />
                {op.libelle}
              </label>
            ))}
          </div>
        </fieldset>

        <Champ id="cand-numero" libelle={t("cand.numero_label")} aide={t("cand.numero_aide")}>
          <Input
            id="cand-numero"
            type="tel"
            inputMode="numeric"
            autoComplete="tel-national"
            placeholder="677123456"
            value={champs.numero_versement}
            onChange={(e) => modifier("numero_versement", chiffresNumeroLocal(e.target.value))}
          />
        </Champ>

        {verifie ? (
          <p role="status" className="flex items-center gap-2 font-medium text-success">
            <Check className="size-4" aria-hidden="true" />
            {t("cand.numero_verifie")}
          </p>
        ) : (
          <div className="flex flex-col gap-3">
            <Button
              type="button"
              variant="outline"
              disabled={!numeroValide || occupe !== null}
              onClick={() => void demanderCode()}
              className="w-fit rounded-full"
            >
              {occupe === "code" && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
              {codeEnvoyeA ? t("cand.renvoyer_code") : t("cand.envoyer_code")}
            </Button>
            {codeEnvoyeA && (
              <div className="flex flex-col gap-2">
                <p className="text-muted-foreground">{t("cand.code_envoye", { numero: codeEnvoyeA })}</p>
                <div className="flex gap-2">
                  <Input
                    aria-label={t("cand.code_label")}
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    maxLength={6}
                    placeholder="123456"
                    value={code}
                    onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                    className="font-mono tracking-widest"
                  />
                  <Button
                    type="button"
                    disabled={code.length !== 6 || occupe !== null}
                    onClick={() => void verifier()}
                    className="shrink-0 rounded-full"
                  >
                    {occupe === "verif" ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : t("cand.verifier")}
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}
      </Carte>

      <Carte titre={t("cand.etape_charte")}>
        <button
          type="button"
          onClick={() => setCharteOuverte((o) => !o)}
          aria-expanded={charteOuverte}
          className="flex w-fit items-center gap-1.5 font-medium text-primary hover:underline"
        >
          <ChevronDown className={cn("size-4 transition-transform", charteOuverte && "rotate-180")} aria-hidden="true" />
          {t("cand.charte_version", { version: charteVersion })}
        </button>
        {charteOuverte && <CharteRevendeur version={charteVersion} />}
        <label className="flex cursor-pointer items-start gap-2.5">
          <input
            type="checkbox"
            checked={charteAcceptee}
            onChange={(e) => setCharteAcceptee(e.target.checked)}
            className="mt-0.5 size-4 shrink-0 accent-primary"
          />
          <span>{t("cand.charte_accepte")}</span>
        </label>
      </Carte>

      {erreur && <p role="alert" className="text-sm text-destructive">{erreur}</p>}
      {info && <p role="status" className="text-sm text-success">{info}</p>}

      <div className="flex flex-wrap gap-3">
        <Button type="submit" size="lg" disabled={occupe !== null} className="rounded-full">
          {occupe === "envoi" && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
          {t("cand.envoyer")}
        </Button>
        <Button type="button" size="lg" variant="outline" disabled={occupe !== null} onClick={() => void brouillon()} className="rounded-full">
          {occupe === "brouillon" && <Loader2 className="size-4 animate-spin" aria-hidden="true" />}
          {t("cand.enregistrer")}
        </Button>
      </div>
    </form>
  )
}

function Champ({ id, libelle, aide, children }: { id: string; libelle: string; aide?: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id}>{libelle}</Label>
      {children}
      {aide && <p className="text-xs text-muted-foreground">{aide}</p>}
    </div>
  )
}
