import { Copy, MessageCircle, Share2 } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { useAuth } from "@/context/AuthContext"
import { trackEvent } from "@/lib/analytics"
import {
  copierLienDePartage, ouvrirWhatsApp, partageNatifPrefere, partagerNativement, type CanalPartage,
} from "@/lib/partage"

interface BoutonPartagerProps {
  /** Chemin de la page à partager (la fiche de l'épreuve ou du cours, jamais le lecteur payant). */
  chemin: string
  /** Accroche du message, sans le lien : « Regarde ce corrigé de Maths BAC C 2023 ». */
  texte: string
  /** Genre de contenu, pour mesurer ce qui se partage. */
  type: "epreuve" | "cours" | "inedite"
  className?: string
  variant?: "outline" | "ghost" | "secondary" | "default"
  size?: "sm" | "default" | "lg"
  libelle?: string
}

/**
 * Sur un téléphone, un clic ouvre le partage natif (WhatsApp, Telegram, SMS...) ; ailleurs un petit
 * menu propose WhatsApp et la copie du lien. Le lien porte le code de parrainage de l'élève connecté.
 */
export function BoutonPartager({ chemin, texte, type, className, variant = "outline", size = "sm", libelle = "Partager" }: BoutonPartagerProps) {
  const { user } = useAuth()
  const donnees = { chemin, texte, codeParrainage: user?.referral_code || undefined }

  function tracer(canal: CanalPartage) {
    trackEvent("contenu_partage", { type, canal })
  }

  async function partagerSurMobile() {
    const resultat = await partagerNativement(donnees)
    if (resultat === "partage") tracer("natif")
    else if (resultat === "indisponible") {
      // Le partage natif a échoué en cours de route : WhatsApp reste un chemin qui marche.
      ouvrirWhatsApp(donnees)
      tracer("whatsapp")
    }
  }

  async function copier() {
    if (await copierLienDePartage(donnees)) {
      toast.success("Lien copié")
      tracer("copie")
    } else {
      toast.error("Impossible de copier le lien")
    }
  }

  const bouton = (
    <Button variant={variant} size={size} className={className} onClick={partageNatifPrefere() ? partagerSurMobile : undefined}>
      <Share2 aria-hidden="true" />
      {libelle}
    </Button>
  )

  if (partageNatifPrefere()) return bouton

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>{bouton}</DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem
          onSelect={() => {
            ouvrirWhatsApp(donnees)
            tracer("whatsapp")
          }}
        >
          <MessageCircle aria-hidden="true" />
          WhatsApp
        </DropdownMenuItem>
        <DropdownMenuItem onSelect={copier}>
          <Copy aria-hidden="true" />
          Copier le lien
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
