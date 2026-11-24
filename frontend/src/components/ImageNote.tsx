import { useEffect, useState } from "react"
import { useQuery } from "@tanstack/react-query"

import { getImageNote } from "@/api/endpoints"
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { t, useI18n } from "@/lib/i18n"

/** Une adresse d'objet pour un Blob, libérée quand il change ou que le composant disparaît. */
function useAdresseBlob(blob: Blob | undefined): string | null {
  const [adresse, setAdresse] = useState<string | null>(null)
  useEffect(() => {
    if (!blob) {
      setAdresse(null)
      return
    }
    const a = URL.createObjectURL(blob)
    setAdresse(a)
    return () => URL.revokeObjectURL(a)
  }, [blob])
  return adresse
}

/**
 * La photo d'une note. Elle est privée : on la lit avec le jeton de connexion (getImageNote) puis on l'affiche depuis le
 * Blob. Un toucher l'ouvre en grand. `version` (la date de la note) renouvelle l'image quand on la remplace.
 */
export function ImageNote({ noteId, version, className }: { noteId: number; version?: string; className?: string }) {
  useI18n()
  const [grand, setGrand] = useState(false)
  const { data, isError } = useQuery({
    queryKey: ["note-image", noteId, version],
    queryFn: ({ signal }) => getImageNote(noteId, signal),
    staleTime: Infinity,
  })
  const adresse = useAdresseBlob(data)
  if (isError) return <p className="text-xs text-muted-foreground">{t("ca.image_erreur")}</p>
  if (!adresse) return <Skeleton className={className ?? "h-40 w-full rounded-xl"} />
  return (
    <>
      <button type="button" onClick={() => setGrand(true)} className="block w-full overflow-hidden rounded-xl border border-border bg-muted/30">
        <img src={adresse} alt={t("ca.image_alt")} loading="lazy" className={className ?? "max-h-64 w-full object-contain"} />
      </button>
      <Dialog open={grand} onOpenChange={setGrand}>
        <DialogContent className="max-w-3xl">
          <DialogTitle className="sr-only">{t("ca.image_alt")}</DialogTitle>
          <img src={adresse} alt={t("ca.image_alt")} className="max-h-[80vh] w-full object-contain" />
        </DialogContent>
      </Dialog>
    </>
  )
}
