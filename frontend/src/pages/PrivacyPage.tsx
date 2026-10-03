import { EyeOff, KeyRound, Lock, ShieldCheck } from "lucide-react"

import { ChipLegale, ListeLegale, PageLegale, PuceLegale, type SectionLegale } from "@/components/PageLegale"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"

// Date de la dernière révision de fond de cette politique - jamais « aujourd'hui » : une date
// qui change toute seule laisserait croire à une mise à jour qui n'a pas eu lieu.
const MISE_A_JOUR = "3 octobre 2026"

const SECTIONS: SectionLegale[] = [
  {
    id: "donnees",
    titre: "Quelles données sont collectées",
    contenu: (
      <>
        <ListeLegale>
          <PuceLegale>
            <strong>Numéro de téléphone</strong> et/ou <strong>adresse e-mail</strong> du titulaire du compte :
            utilisés pour te connecter par code à usage unique (SMS ou e-mail). Aucun mot de passe n'est stocké.
          </PuceLegale>
          <PuceLegale>
            <strong>Identifiant Google</strong>, si tu utilises « Continuer avec Google » : un identifiant technique
            fourni par Google pour reconnaître ton compte - jamais ton mot de passe Google.
          </PuceLegale>
          <PuceLegale>
            <strong>Nom ou pseudo</strong> (optionnels), et <strong>prénom de chaque enfant</strong> pour nommer les
            profils.
          </PuceLegale>
          <PuceLegale>
            <strong>Progression de chaque profil</strong> : épreuves et cours lus, quiz, séances du jour, thèmes à
            réviser, examen préparé - pour t'afficher ta progression et composer ta séance.
          </PuceLegale>
          <PuceLegale>
            <strong>Numéro de l'enfant</strong>, uniquement si le titulaire active sa connexion personnelle, et{" "}
            <strong>codes PIN</strong> des profils et du parent, conservés sous forme chiffrée (hachée) : nous ne
            pouvons pas les lire.
          </PuceLegale>
          <PuceLegale>
            <strong>Données de paiement</strong> : montant, statut et référence de chaque transaction ; pour un
            paiement manuel, aussi l'opérateur, le numéro ayant payé et la référence que tu déclares. Nous ne
            recevons jamais tes identifiants Mobile Money (code secret).
          </PuceLegale>
          <PuceLegale>
            <strong>Adresse IP</strong>, enregistrée lors de l'envoi d'un code de connexion et d'une déclaration de
            paiement, pour limiter les abus et la fraude.
          </PuceLegale>
          <PuceLegale>
            <strong>Évènements d'usage</strong> : quelques actions (début et fin d'un quiz ou d'une épreuve,
            étapes d'un paiement, séance du jour, recherche sans résultat) pour comprendre et améliorer le produit.
            Jamais le texte d'une recherche ni le contenu d'une réponse, seulement le fait que l'action a eu lieu.
          </PuceLegale>
        </ListeLegale>
        <p className="mt-4">
          Tu n'es jamais obligé de fournir toutes ces données : selon la méthode de connexion et les options choisies,
          seules certaines s'appliquent. Nous n'utilisons ni outil d'analyse d'audience tiers (pas de Google
          Analytics) ni pixel publicitaire : les évènements d'usage sont mesurés par notre propre système, jamais
          vendus ni partagés.
        </p>
      </>
    ),
  },
  {
    id: "finalites",
    titre: "Pourquoi ces données",
    contenu: (
      <ListeLegale>
        <PuceLegale>Te permettre de te connecter et de conserver ton accès aux contenus souscrits.</PuceLegale>
        <PuceLegale>Gérer l'abonnement de chaque enfant (durée, examen concerné, paiement).</PuceLegale>
        <PuceLegale>Afficher la progression de chaque profil et composer sa séance de révision quotidienne.</PuceLegale>
        <PuceLegale>
          Envoyer un rappel par e-mail - uniquement si tu l'as activé, sur une adresse confirmée, et que tu peux
          désactiver à tout moment.
        </PuceLegale>
        <PuceLegale>Protéger les comptes et les paiements (limite d'envois de codes, vérification des déclarations).</PuceLegale>
        <PuceLegale>Repérer les points de friction du produit pour l'améliorer, et te répondre si tu contactes le support.</PuceLegale>
      </ListeLegale>
    ),
  },
  {
    id: "enfants",
    titre: "Enfants et familles",
    contenu: (
      <>
        <p>
          Les profils des enfants appartiennent au compte du titulaire, qui les gère. La progression d'un enfant n'est
          visible que depuis son profil : chaque profil peut être protégé par un code PIN, et un enfant qui se
          connecte avec son propre numéro n'accède qu'à son profil, sans voir ceux de ses frères et sœurs ni agir sur
          le compte (paiement, gestion des profils).
        </p>
        <p className="mt-3">
          Le titulaire peut à tout moment modifier ou retirer un code, retirer la connexion personnelle d'un enfant, ou
          demander la suppression de son compte et de ses profils.
        </p>
      </>
    ),
  },
  {
    id: "partage",
    titre: "Avec qui ces données sont partagées",
    contenu: (
      <>
        <ListeLegale>
          <PuceLegale>
            <strong>CamPay</strong>, notre prestataire de paiement Mobile Money, pour le traitement des paiements
            automatiques.
          </PuceLegale>
          <PuceLegale>
            <strong>Google</strong>, si tu choisis « Continuer avec Google » : Google nous transmet un identifiant, ton
            adresse e-mail et ton nom pour ouvrir ou reconnaître ton compte, selon ses propres conditions.
          </PuceLegale>
          <PuceLegale>
            Nos prestataires techniques d'envoi de <strong>SMS</strong> et d'<strong>e-mails</strong>, uniquement pour
            te transmettre ton code de connexion, tes confirmations et, si tu les as activés, tes rappels.
          </PuceLegale>
          <PuceLegale>
            Un service de <strong>suivi des erreurs techniques</strong>, lorsqu'il est activé, pour corriger les
            pannes : il est configuré pour ne pas recevoir de données personnelles.
          </PuceLegale>
        </ListeLegale>
        <p className="mt-4">Nous ne vendons ni ne partageons tes données avec des tiers à des fins publicitaires.</p>
      </>
    ),
  },
  {
    id: "conservation",
    titre: "Durée de conservation",
    contenu: (
      <p>
        Tes données sont conservées tant que ton compte est actif. Tu peux demander la suppression de ton compte et de
        tes données à tout moment (voir les coordonnées ci-dessous). Les données de transaction peuvent être
        conservées plus longtemps lorsque la comptabilité ou la lutte contre la fraude l'exigent.
      </p>
    ),
  },
  {
    id: "droits",
    titre: "Tes droits",
    contenu: (
      <p>
        Depuis ton compte, tu peux rattacher ou détacher une méthode de connexion (la dernière ne peut pas être
        détachée, pour éviter de te retrouver sans accès), gérer les codes et la connexion de tes enfants, et activer
        ou couper les rappels. Pour tout le reste - accès, rectification ou suppression de tes données personnelles -
        contacte-nous à tout moment.
      </p>
    ),
  },
  {
    id: "stockage",
    titre: "Cookies et stockage local",
    contenu: (
      <>
        <p>
          {SITE_NAME} dépose un seul cookie, strictement nécessaire : un cookie de session sécurisé, inaccessible
          au code de la page, qui te garde connecté. Ton navigateur conserve aussi, localement, quelques préférences
          (pays, thème d'affichage) et, pour lire hors connexion, les corrigés que tu as déjà ouverts - effacés
          quand tu te déconnectes.
        </p>
        <p className="mt-3">Aucun cookie publicitaire ou de suivi tiers n'est déposé.</p>
      </>
    ),
  },
]

export function PrivacyPage() {
  useSeo({
    title: "Politique de confidentialité",
    description: `Quelles données ${SITE_NAME} collecte, pourquoi, et comment exercer tes droits.`,
  })

  return (
    <PageLegale
      icone={ShieldCheck}
      titre="Politique de confidentialité"
      introduction={`Quelles données ${SITE_NAME} collecte, pourquoi, avec qui elles sont partagées, et comment exercer tes droits - pour toi et pour tes enfants.`}
      puces={
        <>
          <ChipLegale icone={Lock}>Aucune carte bancaire enregistrée</ChipLegale>
          <ChipLegale icone={EyeOff}>Aucun tracking publicitaire tiers</ChipLegale>
          <ChipLegale icone={KeyRound} className="text-gold-text">Profils protégeables par un code</ChipLegale>
        </>
      }
      miseAJour={MISE_A_JOUR}
      sections={SECTIONS}
      voirAussi={{ to: "/cgu", libelle: "Conditions d'utilisation" }}
    />
  )
}
