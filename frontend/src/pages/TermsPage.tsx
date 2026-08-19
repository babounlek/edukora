import { Link } from "react-router-dom"
import { ArrowLeft, Check, Mail, MessageCircle, ScrollText, ShieldCheck, Wallet } from "lucide-react"

import { useSeo } from "@/lib/seo"
import { SITE_DOMAIN, SITE_NAME } from "@/lib/site"
import { useCountry } from "@/context/CountryContext"
import { epreuvesListPath } from "@/lib/countryPath"

const CONTACT_EMAIL = `contact@${SITE_DOMAIN}`

const SECTIONS = [
  {
    title: "Objet",
    body: (
      <p>
        {SITE_NAME} donne accès à des corrigés d'annales, sujets et cours de révision pour le BEPC, le Probatoire et
        le BAC au Cameroun. L'accès à la lecture en ligne est réservé aux comptes titulaires d'un abonnement actif
        sur le cursus concerné.
      </p>
    ),
  },
  {
    title: "Compte utilisateur",
    body: (
      <p>
        Le compte se crée et s'ouvre par numéro de téléphone camerounais (code à usage unique reçu par SMS), via
        « Continuer avec Google », ou par adresse e-mail (code à usage unique reçu par e-mail). Un même compte peut
        rattacher plusieurs de ces méthodes à la fois - c'est même recommandé, pour ne pas perdre l'accès à ton
        compte en cas de perte du numéro de téléphone. Tu es responsable de la confidentialité de chaque méthode
        rattachée à ton compte (accès à ton téléphone, à ta boîte e-mail, à ton compte Google).
      </p>
    ),
  },
  {
    title: "Contenu gratuit et contenu payant",
    body: (
      <p>
        Les énoncés des sujets sont toujours en libre accès, sans compte ni abonnement. Le corrigé détaillé
        (méthode, résolution, pièges, conseils) et les cours sont réservés aux abonnés actifs sur le cursus
        concerné.
      </p>
    ),
  },
  {
    title: "Abonnement",
    body: (
      <p>
        L'abonnement donne accès à l'ensemble des corrigés et cours d'un cursus (examen et série) donné, pour une
        durée de 1 mois, 3 mois ou 1 an au choix - ou, à l'approche d'une session d'examen, jusqu'au jour de
        l'examen (Pack Examen). Le paiement se fait par Mobile Money via CamPay. L'abonnement
        n'est <strong className="text-foreground">pas reconduit automatiquement</strong> : à son expiration, l'accès
        au corrigé est retiré jusqu'à un nouveau paiement (l'énoncé reste toujours consultable gratuitement).
      </p>
    ),
  },
  {
    title: "Paiement et remboursement",
    body: (
      <p>
        Les paiements sont fermes et non remboursables une fois la transaction confirmée, sauf en cas de
        dysfonctionnement technique avéré de la plateforme empêchant l'accès au contenu souscrit - à signaler
        via le support.
      </p>
    ),
  },
  {
    title: "Propriété intellectuelle",
    body: (
      <p>
        Les corrigés et cours sont réservés à ton usage personnel. Toute reproduction, redistribution ou revente
        est interdite. Le PDF du sujet (énoncé seul) peut en revanche être librement partagé.
      </p>
    ),
  },
  {
    title: "Suspension et résiliation",
    body: (
      <p>
        Tu peux demander la suppression de ton compte à tout moment. Nous nous réservons le droit de suspendre
        un compte en cas d'usage abusif (partage de compte, tentative de contournement du paiement).
      </p>
    ),
  },
  {
    title: "Évolution des présentes conditions",
    body: <p>Ces conditions peuvent évoluer ; la version en vigueur est toujours celle publiée sur cette page.</p>,
  },
  {
    title: "Droit applicable",
    body: <p>Les présentes conditions sont soumises au droit camerounais.</p>,
  },
]

function ChipReassurance({ icon, children }: { icon: React.ReactNode; children: React.ReactNode }) {
  return (
    <span className="flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1.5 text-sm">
      {icon}
      <span className="text-muted-foreground">{children}</span>
    </span>
  )
}

export function TermsPage() {
  useSeo({
    title: "Conditions générales d'utilisation et de vente",
    description: `Fonctionnement des abonnements ${SITE_NAME}, paiement, remboursement et propriété intellectuelle.`,
  })
  const { country } = useCountry()

  return (
    <div className="mx-auto max-w-3xl animate-fade-up px-4 py-8 sm:px-6">
      <Link
        to={epreuvesListPath(country)}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour au catalogue
      </Link>

      <div className="relative mb-8 overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-primary/[0.07] via-transparent to-transparent p-6 sm:p-8">
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: "radial-gradient(circle at 2px 2px, var(--foreground) 1.5px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
        <div className="relative">
          <div className="mb-3 flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <ScrollText className="size-5" />
          </div>
          <p className="mb-1 font-display text-sm italic text-primary">Informations légales</p>
          <h1 className="font-display text-3xl font-semibold leading-[1.15] sm:text-4xl">
            Conditions générales d'utilisation et de vente
          </h1>
          <p className="mt-2 text-muted-foreground">
            Comment fonctionne {SITE_NAME} : accès aux sujets et corrigés, abonnement, paiement et résiliation.
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            <ChipReassurance icon={<Check className="size-3.5 text-success" />}>
              Sujets toujours gratuits
            </ChipReassurance>
            <ChipReassurance icon={<ShieldCheck className="size-3.5 text-success" />}>
              Pas de reconduction automatique
            </ChipReassurance>
            <ChipReassurance icon={<Wallet className="size-3.5 text-gold" />}>
              Résiliable à tout moment
            </ChipReassurance>
          </div>

          <p className="mt-5 text-xs text-muted-foreground">
            Dernière mise à jour : {new Date().toLocaleDateString("fr-FR", { year: "numeric", month: "long" })}
          </p>
        </div>
      </div>

      <div className="border-l border-border">
        {SECTIONS.map((section, index) => (
          <div key={section.title} className="relative py-2 pb-9 pl-9 last:pb-0">
            <span className="absolute -left-4 top-0 flex size-8 items-center justify-center rounded-full border border-border bg-background font-display text-sm font-semibold tabular-nums text-primary">
              {String(index + 1).padStart(2, "0")}
            </span>
            <h2 className="font-display text-base font-semibold">{section.title}</h2>
            <div className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{section.body}</div>
          </div>
        ))}
      </div>

      <div className="mt-4 flex flex-col gap-6 rounded-xl border border-border bg-card p-7 shadow-sm sm:flex-row sm:items-start">
        <span className="flex size-16 shrink-0 items-center justify-center rounded-full bg-primary font-display text-xl font-semibold text-primary-foreground ring-2 ring-gold/50 ring-offset-2 ring-offset-card">
          BSG
        </span>
        <div>
          <h2 className="font-display text-lg font-semibold">BABOUNLEK Serge Guyguy</h2>
          <p className="mt-0.5 text-sm text-muted-foreground">
            Éditeur de la plateforme - Yaoundé, Cameroun - +237 698 19 29 91
          </p>
          <div className="mt-4 flex flex-wrap gap-5">
            <a
              href={`mailto:${CONTACT_EMAIL}`}
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              <Mail className="size-4" />
              {CONTACT_EMAIL}
            </a>
            <a
              href="https://wa.me/237670401393"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              <MessageCircle className="size-4" />
              WhatsApp +237 670 40 13 93
            </a>
          </div>
          <p className="mt-5 border-t border-border pt-4 text-sm text-muted-foreground">
            Voir aussi :{" "}
            <Link to="/confidentialite" className="underline underline-offset-2 hover:text-foreground">
              Politique de confidentialité
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
