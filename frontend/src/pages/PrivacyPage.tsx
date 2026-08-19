import { Link } from "react-router-dom"
import {
  ArrowLeft,
  Clock,
  Cookie,
  Database,
  EyeOff,
  KeyRound,
  Lock,
  Mail,
  MessageCircle,
  Share2,
  ShieldCheck,
  Target,
  UserCog,
} from "lucide-react"

import { useSeo } from "@/lib/seo"
import { SITE_DOMAIN, SITE_NAME } from "@/lib/site"
import { useCountry } from "@/context/CountryContext"
import { epreuvesListPath } from "@/lib/countryPath"

const CONTACT_EMAIL = `contact@${SITE_DOMAIN}`

function Puce({ children }: { children: React.ReactNode }) {
  return (
    <li className="flex gap-2.5">
      <span className="mt-2 size-1.5 shrink-0 rounded-full bg-gold" />
      <span>{children}</span>
    </li>
  )
}

const SECTIONS = [
  {
    icon: Database,
    title: "Quelles données sont collectées",
    body: (
      <>
        <ul className="mt-3 flex flex-col gap-2.5 text-sm leading-relaxed text-muted-foreground">
          <Puce>
            <strong className="text-foreground">Numéro de téléphone</strong> (si tu te connectes par téléphone) :
            utilisé pour l'authentification par code à usage unique reçu par SMS (aucun mot de passe n'est stocké).
          </Puce>
          <Puce>
            <strong className="text-foreground">Adresse e-mail</strong> (si tu te connectes par e-mail, ou via
            « Continuer avec Google ») : utilisée pour l'authentification par code à usage unique, ou transmise par
            Google lors de la connexion.
          </Puce>
          <Puce>
            <strong className="text-foreground">Identifiant Google</strong> (si tu utilises « Continuer avec
            Google ») : un identifiant technique fourni par Google pour reconnaître ton compte - jamais ton mot de
            passe Google, que nous ne voyons à aucun moment.
          </Puce>
          <Puce>
            <strong className="text-foreground">Nom</strong> (optionnel) : si renseigné lors de l'inscription, ou
            transmis par Google.
          </Puce>
          <Puce>
            <strong className="text-foreground">Historique de lecture</strong> : quelles épreuves/cours tu as
            consultés, pour afficher ta progression.
          </Puce>
          <Puce>
            <strong className="text-foreground">Évènements d'usage</strong> : quelques actions liées à ton compte
            (démarrage/fin d'un quiz ou d'une épreuve inédite, étapes d'un paiement, recherche sans résultat), pour
            comprendre et améliorer le produit. Jamais le texte d'une recherche ni le contenu d'une action,
            seulement le fait qu'elle a eu lieu.
          </Puce>
          <Puce>
            <strong className="text-foreground">Données de transaction</strong> : montant, statut et référence de
            chaque paiement d'abonnement, transmises par notre prestataire de paiement Mobile Money (CamPay). Nous
            ne recevons jamais tes identifiants Mobile Money eux-mêmes.
          </Puce>
        </ul>
        <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
          Tu n'es jamais obligé de fournir toutes ces données : selon la méthode de connexion choisie, seules
          certaines s'appliquent. Nous n'utilisons aucun outil d'analyse ou de suivi publicitaire tiers (pas de
          Google Analytics, pas de pixel publicitaire) : les évènements d'usage ci-dessus sont mesurés uniquement
          par notre propre système, jamais vendus ni partagés.
        </p>
      </>
    ),
  },
  {
    icon: Target,
    title: "Pourquoi ces données",
    body: (
      <ul className="mt-3 flex flex-col gap-2.5 text-sm leading-relaxed text-muted-foreground">
        <Puce>Te permettre de te connecter et de conserver ton accès aux contenus souscrits.</Puce>
        <Puce>Gérer ton abonnement (durée, cursus concerné, renouvellement).</Puce>
        <Puce>T'afficher ta progression personnelle (épreuves/cours déjà lus).</Puce>
        <Puce>Comprendre les points de friction du produit (recherche infructueuse, paiement abandonné) pour l'améliorer.</Puce>
        <Puce>Te répondre si tu contactes le support.</Puce>
      </ul>
    ),
  },
  {
    icon: Share2,
    title: "Avec qui ces données sont partagées",
    body: (
      <>
        <ul className="mt-3 flex flex-col gap-2.5 text-sm leading-relaxed text-muted-foreground">
          <Puce>
            <strong className="text-foreground">CamPay</strong>, notre prestataire de paiement Mobile Money, pour le
            traitement de tes paiements d'abonnement.
          </Puce>
          <Puce>
            <strong className="text-foreground">Google</strong>, si tu choisis « Continuer avec Google » : Google
            nous transmet un identifiant, ton adresse e-mail et ton nom pour ouvrir ou reconnaître ton compte, selon
            les conditions de Google elles-mêmes.
          </Puce>
          <Puce>
            Nos prestataires techniques d'envoi de <strong className="text-foreground">SMS</strong> et
            d'<strong className="text-foreground">e-mails</strong>, uniquement pour te transmettre ton code de
            connexion.
          </Puce>
        </ul>
        <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
          Nous ne vendons ni ne partageons tes données avec des tiers à des fins publicitaires.
        </p>
      </>
    ),
  },
  {
    icon: Clock,
    title: "Durée de conservation",
    body: (
      <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
        Tes données sont conservées tant que ton compte est actif. Tu peux demander la suppression de ton compte
        et de tes données à tout moment (voir Contact ci-dessous).
      </p>
    ),
  },
  {
    icon: UserCog,
    title: "Tes droits",
    body: (
      <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
        Depuis les paramètres de ton compte, tu peux toi-même rattacher ou détacher une méthode de connexion
        (téléphone, e-mail, Google) - la dernière méthode restante ne peut pas être détachée, pour éviter de te
        retrouver sans accès. Pour tout le reste (accès, rectification ou suppression de tes données
        personnelles), contacte-nous à tout moment.
      </p>
    ),
  },
  {
    icon: Cookie,
    title: "Cookies et stockage local",
    body: (
      <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
        {SITE_NAME} utilise uniquement le stockage local de ton navigateur pour garder ta session connectée (jeton
        d'authentification). Aucun cookie de suivi publicitaire tiers n'est déposé.
      </p>
    ),
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

export function PrivacyPage() {
  useSeo({
    title: "Politique de confidentialité",
    description: `Quelles données ${SITE_NAME} collecte, pourquoi, et comment les exercer tes droits.`,
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
            <ShieldCheck className="size-5" />
          </div>
          <p className="mb-1 font-display text-sm italic text-primary">Informations légales</p>
          <h1 className="font-display text-3xl font-semibold leading-[1.15] sm:text-4xl">
            Politique de confidentialité
          </h1>
          <p className="mt-2 text-muted-foreground">
            Quelles données {SITE_NAME} collecte, pourquoi, avec qui elles sont partagées, et comment exercer tes
            droits.
          </p>

          <div className="mt-5 flex flex-wrap gap-2">
            <ChipReassurance icon={<Lock className="size-3.5 text-success" />}>
              Aucune carte bancaire enregistrée
            </ChipReassurance>
            <ChipReassurance icon={<EyeOff className="size-3.5 text-success" />}>
              Aucun tracking publicitaire tiers
            </ChipReassurance>
            <ChipReassurance icon={<KeyRound className="size-3.5 text-gold" />}>
              Tu gères tes méthodes de connexion
            </ChipReassurance>
          </div>

          <p className="mt-5 text-xs text-muted-foreground">
            Dernière mise à jour : {new Date().toLocaleDateString("fr-FR", { year: "numeric", month: "long" })}
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-5">
        {SECTIONS.map((section) => (
          <div key={section.title} className="rounded-xl border border-border bg-card p-6 shadow-sm">
            <div className="flex items-center gap-3">
              <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-accent text-primary">
                <section.icon className="size-5" />
              </span>
              <h2 className="font-display text-lg font-semibold">{section.title}</h2>
            </div>
            {section.body}
          </div>
        ))}
      </div>

      <div className="mt-5 flex flex-col gap-6 rounded-xl border border-border bg-card p-7 shadow-sm sm:flex-row sm:items-start">
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
            <Link to="/cgu" className="underline underline-offset-2 hover:text-foreground">
              Conditions d'utilisation
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
