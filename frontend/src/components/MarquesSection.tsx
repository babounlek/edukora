import { useState } from "react"
import { Bookmark, Check, PenLine } from "lucide-react"

import { Button } from "@/components/ui/button"
import type { Etude } from "@/lib/useEtude"
import { cn } from "@/lib/utils"

const NOTE_MAX = 2000

/**
 * La barre d'outils d'étude d'une section : "j'ai compris", signet, note personnelle.
 *
 * "Compris" est DÉCLARÉ, jamais déduit d'un défilement (même règle que "Je l'ai fait" sur
 * un exercice) : un suivi qu'on remplit sans travailler ne mesure plus rien. `avecCompris`
 * est faux sur les exercices d'épreuve, qui ont déjà leur propre validation
 * ("Exercice validé") - deux cases pour la même chose se contrediraient.
 *
 * Absente pour un visiteur anonyme (voir useEtude.disponible) : sans compte, il n'y a nulle
 * part où ranger une note.
 */
export function MarquesSection({
  etude, cle, avecCompris = true, className,
}: { etude: Etude; cle: string; avecCompris?: boolean; className?: string }) {
  const marque = etude.marques[cle]
  const [ouvert, setOuvert] = useState(false)
  const [brouillon, setBrouillon] = useState("")

  if (!etude.disponible) return null

  const note = marque?.note ?? ""

  function ouvrirNote() {
    setBrouillon(note)
    setOuvert(true)
  }

  function enregistrerNote() {
    if (brouillon.trim() !== note) etude.maj(cle, { note: brouillon.trim() })
    setOuvert(false)
  }

  return (
    <div className={cn("not-prose mt-4", className)}>
      <div className="flex flex-wrap items-center gap-2">
        {avecCompris && (
          <Button
            type="button"
            size="sm"
            variant={marque?.compris ? "default" : "outline"}
            aria-pressed={Boolean(marque?.compris)}
            onClick={() => etude.maj(cle, { compris: !marque?.compris })}
            className="rounded-full"
          >
            <Check className="size-4" />
            {marque?.compris ? "Compris" : "J'ai compris"}
          </Button>
        )}
        <Button
          type="button"
          size="sm"
          variant="ghost"
          aria-pressed={Boolean(marque?.signet)}
          onClick={() => etude.maj(cle, { signet: !marque?.signet })}
          className={cn("rounded-full", marque?.signet ? "text-gold-foreground dark:text-gold" : "text-muted-foreground")}
        >
          <Bookmark className={cn("size-4", marque?.signet && "fill-current")} />
          {marque?.signet ? "Gardé pour plus tard" : "Garder pour plus tard"}
        </Button>
        {!ouvert && (
          <Button
            type="button"
            size="sm"
            variant="ghost"
            onClick={ouvrirNote}
            className="rounded-full text-muted-foreground"
          >
            <PenLine className="size-4" />
            {note ? "Modifier ma note" : "Ajouter une note"}
          </Button>
        )}
      </div>

      {!ouvert && note && (
        <p className="mt-3 whitespace-pre-wrap rounded-xl border border-gold/30 bg-gold/[0.06] px-4 py-3 text-sm leading-relaxed">
          {note}
        </p>
      )}

      {ouvert && (
        <div className="mt-3 flex flex-col gap-2">
          <label htmlFor={`note-${cle}`} className="sr-only">
            Ma note sur cette section
          </label>
          <textarea
            id={`note-${cle}`}
            value={brouillon}
            onChange={(e) => setBrouillon(e.target.value)}
            maxLength={NOTE_MAX}
            rows={4}
            autoFocus
            placeholder="Ce que tu veux retenir, un piège à éviter, une question à poser…"
            className="w-full resize-y rounded-xl border border-input bg-background px-3.5 py-2.5 text-sm leading-relaxed outline-none transition-colors focus-visible:border-primary focus-visible:ring-2 focus-visible:ring-ring/40"
          />
          <div className="flex flex-wrap items-center gap-2">
            <Button type="button" size="sm" onClick={enregistrerNote} className="rounded-full">
              Enregistrer
            </Button>
            <Button type="button" size="sm" variant="ghost" onClick={() => setOuvert(false)} className="rounded-full">
              Annuler
            </Button>
            {note && (
              <Button
                type="button"
                size="sm"
                variant="ghost"
                onClick={() => {
                  etude.maj(cle, { note: "" })
                  setOuvert(false)
                }}
                className="rounded-full text-destructive"
              >
                Supprimer la note
              </Button>
            )}
            <span className="ml-auto text-xs tabular-nums text-muted-foreground">
              {brouillon.length} / {NOTE_MAX}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
