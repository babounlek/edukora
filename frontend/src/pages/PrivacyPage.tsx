import { Link } from "react-router-dom"
import { ArrowLeft } from "lucide-react"

import { useSeo } from "@/lib/seo"
import { SITE_DOMAIN, SITE_NAME } from "@/lib/site"

const CONTACT_EMAIL = `contact@${SITE_DOMAIN}`

export function PrivacyPage() {
  useSeo({
    title: "Politique de confidentialité",
    description: `Quelles données ${SITE_NAME} collecte, pourquoi, et comment les exercer tes droits.`,
  })

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <Link
        to="/"
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour au catalogue
      </Link>

      <article className="prose prose-neutral max-w-none dark:prose-invert prose-headings:font-display">
        <h1 className="font-display">Politique de confidentialité</h1>
        <p className="text-sm text-muted-foreground">Dernière mise à jour : {new Date().toLocaleDateString("fr-FR", { year: "numeric", month: "long" })}</p>

        <h2>Éditeur de la plateforme</h2>
        <p>BABOUNLEK Serge Guyguy, entrepreneur individuel - Yaoundé, Cameroun - +237 698 19 29 91</p>

        <h2>Quelles données sont collectées</h2>
        <ul>
          <li><strong>Numéro de téléphone</strong> : identifiant de compte, utilisé pour l'authentification par code à usage unique (aucun mot de passe n'est stocké).</li>
          <li><strong>Nom</strong> (optionnel) : si renseigné lors de l'inscription.</li>
          <li><strong>Historique de lecture</strong> : quelles leçons/cours tu as consultés, pour afficher ta progression.</li>
          <li><strong>Données de transaction</strong> : montant, statut et référence de chaque paiement d'abonnement, transmises par notre prestataire de paiement Mobile Money (CamPay). Nous ne recevons jamais tes identifiants Mobile Money eux-mêmes.</li>
        </ul>
        <p>Nous ne collectons pas d'adresse email et n'utilisons aujourd'hui aucun outil d'analyse ou de suivi publicitaire tiers.</p>

        <h2>Pourquoi ces données</h2>
        <ul>
          <li>Te permettre de te connecter et de conserver ton accès aux contenus souscrits.</li>
          <li>Gérer ton abonnement (durée, cursus concerné, renouvellement).</li>
          <li>T'afficher ta progression personnelle (leçons/cours déjà lus).</li>
          <li>Te répondre si tu contactes le support.</li>
        </ul>

        <h2>Avec qui ces données sont partagées</h2>
        <p>
          Uniquement avec <strong>CamPay</strong>, notre prestataire de paiement Mobile Money, pour le traitement
          de tes paiements d'abonnement. Nous ne vendons ni ne partageons tes données avec des tiers à des fins
          publicitaires.
        </p>

        <h2>Durée de conservation</h2>
        <p>
          Tes données sont conservées tant que ton compte est actif. Tu peux demander la suppression de ton compte
          et de tes données à tout moment (voir Contact ci-dessous).
        </p>

        <h2>Tes droits</h2>
        <p>
          Tu peux demander l'accès, la rectification ou la suppression de tes données personnelles à tout moment
          en nous contactant.
        </p>

        <h2>Cookies et stockage local</h2>
        <p>
          {SITE_NAME} utilise uniquement le stockage local de ton navigateur pour garder ta session connectée (jeton
          d'authentification). Aucun cookie de suivi publicitaire tiers n'est déposé.
        </p>

        <h2>Contact</h2>
        <p>
          Pour toute question sur tes données : <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> ou{" "}
          <a href="https://wa.me/237670401393" target="_blank" rel="noopener noreferrer">WhatsApp +237 670 40 13 93</a>.
        </p>
      </article>
    </div>
  )
}
