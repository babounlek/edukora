import { Check, ScrollText, ShieldCheck, Smartphone } from "lucide-react"

import { ChipLegale, ListeLegale, PageLegale, PuceLegale, type SectionLegale } from "@/components/PageLegale"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import { delaiVerificationPaiementAffiche } from "@/lib/delaiVerificationPaiement"
import { dateLegale } from "@/lib/dateLegale"
import { t, useI18n } from "@/lib/i18n"
import { texteRiche } from "@/lib/texteRiche"

// Date de la dernière révision de fond de ces conditions - jamais « aujourd'hui » : une date
// qui change toute seule laisserait croire à une mise à jour qui n'a pas eu lieu.
const MISE_A_JOUR = "2026-10-03"

// Construites au rendu (et non au chargement du module) pour suivre la langue courante.
function sections(): SectionLegale[] {
  const site = SITE_NAME
  return [
    {
      id: "objet",
      titre: t("cgu.objet_titre"),
      contenu: <p>{t("cgu.objet", { site })}</p>,
    },
    {
      id: "compte",
      titre: t("cgu.compte_titre"),
      contenu: (
        <>
          <p>{t("cgu.compte1")}</p>
          <p className="mt-3">{texteRiche(t("cgu.compte2"))}</p>
          <ListeLegale>
            <PuceLegale>{texteRiche(t("cgu.compte_pin"))}</PuceLegale>
            <PuceLegale>{t("cgu.compte_enfant")}</PuceLegale>
          </ListeLegale>
        </>
      ),
    },
    {
      id: "contenu",
      titre: t("cgu.contenu_titre"),
      contenu: <p>{t("cgu.contenu")}</p>,
    },
    {
      id: "abonnement",
      titre: t("cgu.abo_titre"),
      contenu: (
        <>
          <p>{texteRiche(t("cgu.abo1"))}</p>
          <ListeLegale>
            <PuceLegale>{texteRiche(t("cgu.abo_prix1"))}</PuceLegale>
            <PuceLegale>{texteRiche(t("cgu.abo_prix2"))}</PuceLegale>
          </ListeLegale>
          <p className="mt-3">{texteRiche(t("cgu.abo3"))}</p>
        </>
      ),
    },
    {
      id: "paiement",
      titre: t("cgu.paiement_titre"),
      contenu: (
        <>
          <p>{t("cgu.paiement1", { delai: delaiVerificationPaiementAffiche() })}</p>
          <p className="mt-3">{t("cgu.paiement2")}</p>
        </>
      ),
    },
    {
      id: "propriete",
      titre: t("cgu.propriete_titre"),
      contenu: <p>{t("cgu.propriete")}</p>,
    },
    {
      id: "suspension",
      titre: t("cgu.suspension_titre"),
      contenu: <p>{t("cgu.suspension")}</p>,
    },
    {
      id: "evolution",
      titre: t("cgu.evolution_titre"),
      contenu: <p>{t("cgu.evolution")}</p>,
    },
    {
      id: "droit",
      titre: t("cgu.droit_titre"),
      contenu: <p>{t("cgu.droit")}</p>,
    },
  ]
}

export function TermsPage() {
  useI18n()
  useSeo({
    title: t("cgu.titre"),
    description: t("cgu.description", { site: SITE_NAME }),
  })

  return (
    <PageLegale
      icone={ScrollText}
      titre={t("cgu.titre")}
      introduction={t("cgu.intro", { site: SITE_NAME })}
      puces={
        <>
          <ChipLegale icone={Check}>{t("cgu.chip1")}</ChipLegale>
          <ChipLegale icone={ShieldCheck}>{t("cgu.chip2")}</ChipLegale>
          <ChipLegale icone={Smartphone} className="text-gold-text">{t("cgu.chip3")}</ChipLegale>
        </>
      }
      miseAJour={dateLegale(MISE_A_JOUR)}
      sections={sections()}
      voirAussi={{ to: "/confidentialite", libelle: t("cgu.voir_aussi") }}
    />
  )
}
