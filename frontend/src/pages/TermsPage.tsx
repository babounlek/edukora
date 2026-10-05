import { Check, ScrollText, ShieldCheck, Smartphone } from "lucide-react"

import { ChipLegale, ListeLegale, PageLegale, PuceLegale, type SectionLegale } from "@/components/PageLegale"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"

// Date de la dernière révision de fond de ces conditions - jamais « aujourd'hui » : une date
// qui change toute seule laisserait croire à une mise à jour qui n'a pas eu lieu.
const MISE_A_JOUR = "3 octobre 2026"

const SECTIONS: SectionLegale[] = [
  {
    id: "objet",
    titre: "Objet",
    contenu: (
      <p>
        {SITE_NAME} aide les élèves à préparer le BEPC, le Probatoire et le BAC au Cameroun : corrigés d'annales et
        de sujets, cours de révision, quiz d'auto-évaluation, parcours par matière, épreuves inédites et séance de
        révision quotidienne. L'accès à ces contenus est réservé aux comptes titulaires d'un abonnement actif pour
        l'examen concerné, à l'exception de ceux proposés en libre accès (voir « Contenu gratuit et contenu payant »).
      </p>
    ),
  },
  {
    id: "compte",
    titre: "Compte et profils",
    contenu: (
      <>
        <p>
          Le compte s'ouvre par numéro de téléphone (code à usage unique reçu par SMS), par « Continuer avec Google »
          ou par adresse e-mail (code à usage unique reçu par e-mail). Plusieurs méthodes peuvent être rattachées au
          même compte - c'est recommandé, pour ne pas perdre l'accès en cas de perte du numéro. Le titulaire est
          responsable de la confidentialité de chacune d'elles.
        </p>
        <p className="mt-3">
          Un compte peut regrouper plusieurs <strong>profils</strong>, un par enfant : chacun a sa propre progression,
          son propre abonnement et sa propre séance du jour. Le titulaire du compte gère les profils de ses enfants
          et reste responsable de leur usage de la plateforme.
        </p>
        <ListeLegale>
          <PuceLegale>
            Un <strong>code PIN à 4 chiffres</strong> peut protéger chaque profil, et un <strong>code parent</strong>{" "}
            peut réserver au titulaire les paiements et la gestion des profils. Ces codes sont facultatifs ; il
            appartient au titulaire de les définir et de les garder confidentiels.
          </PuceLegale>
          <PuceLegale>
            Un enfant qui a son propre téléphone peut se connecter lui-même, avec son numéro vérifié par le titulaire :
            sa session est alors limitée à son profil, sans changement d'enfant ni paiement.
          </PuceLegale>
        </ListeLegale>
      </>
    ),
  },
  {
    id: "contenu",
    titre: "Contenu gratuit et contenu payant",
    contenu: (
      <p>
        Une sélection de contenus est en libre accès, sans abonnement : certains sujets et corrigés présentés en
        vitrine, ainsi que le PDF de l'énoncé d'un sujet, que tu peux partager librement. Le reste - corrigés
        détaillés, cours, quiz, parcours, épreuves inédites et séance du jour - est réservé aux abonnés actifs sur
        l'examen concerné.
      </p>
    ),
  },
  {
    id: "abonnement",
    titre: "Abonnement et prix",
    contenu: (
      <>
        <p>
          Il n'existe qu'une seule formule, <strong>Jusqu'à l'examen</strong> : l'accès est valable pour un enfant et
          un examen donnés, de la date du paiement jusqu'à la fin de la session d'examen visée. Les épreuves inédites
          y sont incluses.
        </p>
        <ListeLegale>
          <PuceLegale>
            <strong>15 000 FCFA</strong> par enfant, quelle que soit la date d'achat dans l'année scolaire.
          </PuceLegale>
          <PuceLegale>
            <strong>12 000 FCFA</strong> pour chaque enfant supplémentaire de la même famille (réduction fixe de
            20 % sur le prix de référence, identique pour le 2<sup>e</sup>, le 3<sup>e</sup>, le 4<sup>e</sup> enfant,
            et ainsi de suite). Exemple : 2 enfants, 27 000 FCFA ; 3 enfants, 39 000 FCFA.
          </PuceLegale>
        </ListeLegale>
        <p className="mt-3">
          L'abonnement n'est <strong>pas reconduit automatiquement</strong> : à son terme, l'accès réservé aux abonnés
          est retiré jusqu'à un nouveau paiement. Aucun prélèvement n'est effectué sans ta demande.
        </p>
      </>
    ),
  },
  {
    id: "paiement",
    titre: "Paiement et remboursement",
    contenu: (
      <>
        <p>
          Le paiement se fait par Mobile Money (MTN MoMo, Orange Money). Deux modes sont proposés : le paiement
          automatique via notre prestataire CamPay, qui active l'accès en quelques secondes, ou le paiement manuel -
          tu transfères toi-même le montant au numéro indiqué puis tu déclares ta transaction, que notre équipe
          vérifie, généralement en quelques heures, avant d'activer l'accès. Tu suis l'état de tes déclarations dans
          « Mes paiements ».
        </p>
        <p className="mt-3">
          Les paiements sont fermes et non remboursables une fois la transaction confirmée, sauf en cas de
          dysfonctionnement technique avéré de la plateforme empêchant l'accès au contenu souscrit - à signaler au
          support.
        </p>
      </>
    ),
  },
  {
    id: "propriete",
    titre: "Propriété intellectuelle",
    contenu: (
      <p>
        Les corrigés, cours, quiz et épreuves inédites sont réservés à ton usage personnel. Toute reproduction,
        redistribution ou revente est interdite. Le PDF d'un sujet (énoncé seul) peut en revanche être librement
        partagé.
      </p>
    ),
  },
  {
    id: "suspension",
    titre: "Suspension et résiliation",
    contenu: (
      <p>
        Tu peux demander la suppression de ton compte à tout moment. Nous nous réservons le droit de suspendre un compte
        en cas d'usage abusif : partage de l'accès d'un enfant avec des tiers, tentative de contournement du paiement,
        déclaration de paiement frauduleuse.
      </p>
    ),
  },
  {
    id: "evolution",
    titre: "Évolution des présentes conditions",
    contenu: <p>Ces conditions peuvent évoluer ; la version en vigueur est toujours celle publiée sur cette page.</p>,
  },
  {
    id: "droit",
    titre: "Droit applicable",
    contenu: <p>Les présentes conditions sont soumises au droit camerounais.</p>,
  },
]

export function TermsPage() {
  useSeo({
    title: "Conditions générales d'utilisation et de vente",
    description: `Fonctionnement de l'abonnement ${SITE_NAME}, prix, paiement, remboursement et propriété intellectuelle.`,
  })

  return (
    <PageLegale
      icone={ScrollText}
      titre="Conditions générales d'utilisation et de vente"
      introduction={`Comment fonctionne ${SITE_NAME} : comptes et profils, abonnement, prix, paiement et résiliation.`}
      puces={
        <>
          <ChipLegale icone={Check}>Un seul prix, jusqu'à l'examen</ChipLegale>
          <ChipLegale icone={ShieldCheck}>Pas de reconduction automatique</ChipLegale>
          <ChipLegale icone={Smartphone} className="text-gold-text">Paiement Mobile Money</ChipLegale>
        </>
      }
      miseAJour={MISE_A_JOUR}
      sections={SECTIONS}
      voirAussi={{ to: "/confidentialite", libelle: "Politique de confidentialité" }}
    />
  )
}
