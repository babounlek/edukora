import { localeCourante } from "@/lib/i18n"

/** Date ISO (`2026-10-03`) écrite en toutes lettres dans la langue courante. Midi pour que le fuseau ne décale pas le jour. */
export function dateLegale(iso: string): string {
  return new Date(`${iso}T12:00:00`).toLocaleDateString(localeCourante(), {
    day: "numeric",
    month: "long",
    year: "numeric",
  })
}
