import { Link } from "react-router-dom"
import { ArrowLeft } from "lucide-react"

import { useSeo } from "@/lib/seo"
import { SITE_DOMAIN, SITE_NAME } from "@/lib/site"
import { useCountry } from "@/context/CountryContext"
import { catalogueHomePath } from "@/lib/countryPath"

const CONTACT_EMAIL = `contact@${SITE_DOMAIN}`

export function TermsPage() {
  useSeo({
    title: "Conditions générales d'utilisation et de vente",
    description: `Fonctionnement des abonnements ${SITE_NAME}, paiement, remboursement et propriété intellectuelle.`,
  })
  const { country } = useCountry()

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <Link
        to={catalogueHomePath(country)}
        className="mb-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-primary"
      >
        <ArrowLeft className="size-4" />
        Retour au catalogue
      </Link>

      <article className="prose prose-neutral max-w-none dark:prose-invert prose-headings:font-display">
        <h1 className="font-display">Conditions générales d'utilisation et de vente</h1>
        <p className="text-sm text-muted-foreground">Dernière mise à jour : {new Date().toLocaleDateString("fr-FR", { year: "numeric", month: "long" })}</p>

        <h2>Éditeur de la plateforme</h2>
        <p>BABOUNLEK Serge Guyguy, entrepreneur individuel - Yaoundé, Cameroun - +237 698 19 29 91</p>

        <h2>1. Objet</h2>
        <p>
          {SITE_NAME} donne accès à des corrigés d'annales, sujets et cours de révision pour le BEPC, le Probatoire et
          le BAC au Cameroun. L'accès à la lecture en ligne est réservé aux comptes titulaires d'un abonnement actif
          sur le cursus concerné.
        </p>

        <h2>2. Compte utilisateur</h2>
        <p>
          La création de compte se fait par numéro de téléphone camerounais et code à usage unique reçu par SMS.
          Un compte correspond à un seul numéro de téléphone. Tu es responsable de la confidentialité de l'accès à
          ton téléphone, seul moyen d'authentification.
        </p>

        <h2>3. Contenu gratuit et contenu payant</h2>
        <p>
          Les énoncés des sujets sont toujours en libre accès, sans compte ni abonnement. Le corrigé détaillé
          (méthode, résolution, pièges, conseils) et les cours sont réservés aux abonnés actifs sur le cursus
          concerné.
        </p>

        <h2>4. Abonnement</h2>
        <p>
          L'abonnement donne accès à l'ensemble des corrigés et cours d'un cursus (examen et série) donné, pour une
          durée de 7 jours, 1 mois ou 1 an au choix. Le paiement se fait par Mobile Money via CamPay. L'abonnement
          n'est <strong>pas reconduit automatiquement</strong> : à son expiration, l'accès au corrigé est retiré
          jusqu'à un nouveau paiement (l'énoncé reste toujours consultable gratuitement).
        </p>

        <h2>5. Paiement et remboursement</h2>
        <p>
          Les paiements sont fermes et non remboursables une fois la transaction confirmée, sauf en cas de
          dysfonctionnement technique avéré de la plateforme empêchant l'accès au contenu souscrit - à signaler
          via le support.
        </p>

        <h2>6. Propriété intellectuelle</h2>
        <p>
          Les corrigés et cours sont réservés à ton usage personnel. Toute reproduction, redistribution ou revente
          est interdite. Le PDF du sujet (énoncé seul) peut en revanche être librement partagé.
        </p>

        <h2>7. Suspension et résiliation</h2>
        <p>
          Tu peux demander la suppression de ton compte à tout moment. Nous nous réservons le droit de suspendre
          un compte en cas d'usage abusif (partage de compte, tentative de contournement du paiement).
        </p>

        <h2>8. Évolution des présentes conditions</h2>
        <p>
          Ces conditions peuvent évoluer ; la version en vigueur est toujours celle publiée sur cette page.
        </p>

        <h2>9. Droit applicable</h2>
        <p>Les présentes conditions sont soumises au droit camerounais.</p>

        <h2>Contact</h2>
        <p>
          <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> ou{" "}
          <a href="https://wa.me/237670401393" target="_blank" rel="noopener noreferrer">WhatsApp +237 670 40 13 93</a>.
        </p>
      </article>
    </div>
  )
}
