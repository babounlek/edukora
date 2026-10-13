import { EyeOff, KeyRound, Lock, ShieldCheck } from "lucide-react"

import { ChipLegale, ListeLegale, PageLegale, PuceLegale, type SectionLegale } from "@/components/PageLegale"
import { useSeo } from "@/lib/seo"
import { SITE_NAME } from "@/lib/site"
import { dateLegale } from "@/lib/dateLegale"
import { t, useI18n } from "@/lib/i18n"
import { texteRiche } from "@/lib/texteRiche"

// Date de la dernière révision de fond de cette politique - jamais « aujourd'hui » : une date
// qui change toute seule laisserait croire à une mise à jour qui n'a pas eu lieu.
const MISE_A_JOUR = "2026-10-03"

// Construites au rendu (et non au chargement du module) pour suivre la langue courante.
function sections(): SectionLegale[] {
  const puces = (prefixe: string, n: number) =>
    Array.from({ length: n }, (_, i) => (
      <PuceLegale key={i}>{texteRiche(t(`${prefixe}${i + 1}` as Parameters<typeof t>[0]))}</PuceLegale>
    ))
  return [
    {
      id: "donnees",
      titre: t("conf.donnees_titre"),
      contenu: (
        <>
          <ListeLegale>{puces("conf.d", 8)}</ListeLegale>
          <p className="mt-4">{t("conf.donnees_fin")}</p>
        </>
      ),
    },
    {
      id: "finalites",
      titre: t("conf.finalites_titre"),
      contenu: <ListeLegale>{puces("conf.f", 6)}</ListeLegale>,
    },
    {
      id: "enfants",
      titre: t("conf.enfants_titre"),
      contenu: (
        <>
          <p>{t("conf.enfants1")}</p>
          <p className="mt-3">{t("conf.enfants2")}</p>
        </>
      ),
    },
    {
      id: "partage",
      titre: t("conf.partage_titre"),
      contenu: (
        <>
          <ListeLegale>{puces("conf.p", 4)}</ListeLegale>
          <p className="mt-4">{t("conf.partage_fin")}</p>
        </>
      ),
    },
    {
      id: "conservation",
      titre: t("conf.conservation_titre"),
      contenu: <p>{t("conf.conservation")}</p>,
    },
    {
      id: "droits",
      titre: t("conf.droits_titre"),
      contenu: <p>{t("conf.droits")}</p>,
    },
    {
      id: "stockage",
      titre: t("conf.stockage_titre"),
      contenu: (
        <>
          <p>{t("conf.stockage1", { site: SITE_NAME })}</p>
          <p className="mt-3">{t("conf.stockage2")}</p>
        </>
      ),
    },
  ]
}

export function PrivacyPage() {
  useI18n()
  useSeo({
    title: t("conf.titre"),
    description: t("conf.description", { site: SITE_NAME }),
  })

  return (
    <PageLegale
      icone={ShieldCheck}
      titre={t("conf.titre")}
      introduction={t("conf.intro", { site: SITE_NAME })}
      puces={
        <>
          <ChipLegale icone={Lock}>{t("conf.chip1")}</ChipLegale>
          <ChipLegale icone={EyeOff}>{t("conf.chip2")}</ChipLegale>
          <ChipLegale icone={KeyRound} className="text-gold-text">{t("conf.chip3")}</ChipLegale>
        </>
      }
      miseAJour={dateLegale(MISE_A_JOUR)}
      sections={sections()}
      voirAussi={{ to: "/cgu", libelle: t("conf.voir_aussi") }}
    />
  )
}
