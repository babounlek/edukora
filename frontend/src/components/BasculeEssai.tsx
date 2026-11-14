import { useState } from "react"
import { Eye, Lightbulb } from "lucide-react"

import { cn } from "@/lib/utils"
import { t, useI18n } from "@/lib/i18n"

/**
 * La préférence « Essaie d'abord » du lecteur d'ÉPREUVE, mémorisée d'une visite à l'autre. Simple confort
 * d'affichage, jamais une donnée à garantir : tout accès au stockage est protégé.
 *
 * Éteinte par défaut, à la différence du lecteur d'exercice par thème (sa propre clé, allumée par défaut) : ici
 * l'élève vient d'abord LIRE un corrigé, et le corrigé reste ouvert tant qu'il n'a pas demandé à chercher
 * d'abord (décision du 2026-11-13).
 */
const CLE = "edukora_epreuve_essai_dabord"

export function lireEssaiEpreuve(): boolean {
  try {
    return window.localStorage.getItem(CLE) === "1"
  } catch {
    return false
  }
}

function ecrireEssaiEpreuve(valeur: boolean) {
  try {
    window.localStorage.setItem(CLE, valeur ? "1" : "0")
  } catch {
    // stockage indisponible : le mode vaut pour cette visite seulement
  }
}

/** L'état « Essaie d'abord » du lecteur d'épreuve et de quoi le changer (mémorisé). */
export function useEssaiEpreuve(): [boolean, (valeur: boolean) => void] {
  const [essai, setEssai] = useState(lireEssaiEpreuve)
  return [
    essai,
    (valeur: boolean) => {
      setEssai(valeur)
      ecrireEssaiEpreuve(valeur)
    },
  ]
}

/**
 * Les deux modes de lecture d'un corrigé : « Essaie d'abord » (les corrigés sont repliés, l'élève cherche puis
 * dévoile) et « Tout afficher ». Même libellés et même dessin que la bascule du lecteur par thème.
 */
export function BasculeEssai({
  essai, onChange, className,
}: { essai: boolean; onChange: (valeur: boolean) => void; className?: string }) {
  useI18n()
  return (
    <div
      role="group"
      aria-label={t("tl.mode_aria")}
      className={cn("inline-flex rounded-full border border-border bg-muted/50 p-1", className)}
    >
      <Mode actif={essai} onClick={() => onChange(true)}>
        <Lightbulb className="size-3.5" aria-hidden="true" />
        {t("tl.essaie")}
      </Mode>
      <Mode actif={!essai} onClick={() => onChange(false)}>
        <Eye className="size-3.5" aria-hidden="true" />
        {t("tl.tout_afficher")}
      </Mode>
    </div>
  )
}

function Mode({ actif, onClick, children }: { actif: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={actif}
      className={cn(
        "inline-flex min-h-9 items-center gap-1.5 rounded-full px-3 text-sm font-medium transition-colors",
        actif ? "bg-card text-primary shadow-sm" : "text-muted-foreground hover:text-foreground",
      )}
    >
      {children}
    </button>
  )
}
