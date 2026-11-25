import type { CarnetEntree } from "@/api/types"
import { ImageNote } from "@/components/ImageNote"
import { NoteTexte } from "@/components/NoteTexte"
import { libelleSection } from "@/components/notes/CarteNote"
import { SITE_NAME } from "@/lib/site"
import { cn } from "@/lib/utils"
import { localeCourante, t, tn, useI18n } from "@/lib/i18n"

// Au-delà, une note prend toute la largeur de la page : en demi-colonne elle ferait un long ruban difficile à relire.
const LONGUE = 520

/**
 * La feuille qui sort de l'imprimante quand l'élève imprime un dossier de notes. Elle n'existe QUE sur papier (masquée à
 * l'écran) et remplace la page : la mise en page de l'écran, faite pour le doigt, imprime mal.
 *
 * Pensée pour celui qui imprime : une page se paie à l'unité au cybercafé, presque toujours en noir et blanc. Donc deux
 * colonnes serrées, aucune couleur ni aplat (rien qui boive de l'encre), des filets fins, et tout ce qui ne sert qu'à
 * l'écran (boutons, pastilles, liens) est absent. En tête : la matière, le nom de l'élève, la date. Une case à cocher par
 * note permet de réviser crayon en main (« je la sais »). Une note ne se coupe jamais entre deux pages.
 */
export function NotesImprimees({
  titre, entrees, eleve, examen,
}: { titre: string; entrees: CarnetEntree[]; eleve?: string; examen?: string }) {
  useI18n()
  if (entrees.length === 0) return null
  const date = new Date().toLocaleDateString(localeCourante(), { day: "numeric", month: "long", year: "numeric" })
  return (
    <div className="notes-imprimees hidden text-black print:block">
      <div className="flex items-end justify-between gap-6 border-b-2 border-black pb-2">
        <div className="min-w-0">
          <p className="font-sans text-[8pt] font-semibold uppercase tracking-[0.2em]">{t("imp.surtitre")}</p>
          <p className="font-display text-[20pt] font-semibold leading-tight">{titre}</p>
        </div>
        <div className="shrink-0 text-right font-sans text-[8.5pt] leading-snug">
          {eleve && <p className="font-semibold">{eleve}</p>}
          {examen && <p>{examen}</p>}
          <p>
            {tn("ca.stat_notes", entrees.length)} · {date}
          </p>
        </div>
      </div>

      <ol className="mt-3 list-none columns-2 gap-[9mm] p-0 [column-rule:0.5pt_solid_#bbb]">
        {entrees.map((entree, i) => {
          const longue = (entree.note?.length ?? 0) + (entree.citation?.length ?? 0) > LONGUE || Boolean(entree.a_image)
          return (
            <li
              key={`${entree.genre}-${entree.id}`}
              className={cn("mb-[3mm] break-inside-avoid border-b border-neutral-400 pb-[3mm] text-[10pt] leading-[1.38]", longue && "[column-span:all]")}
            >
              <div className="flex items-baseline gap-1.5">
                <span className="font-sans text-[8.5pt] font-bold tabular-nums">{i + 1}.</span>
                <span className="min-w-0 flex-1 font-sans text-[8pt] font-semibold uppercase tracking-wide text-neutral-700">
                  {entree.type === "libre"
                    ? entree.origine === "quiz"
                      ? t("ca.type_quiz")
                      : entree.origine === "fiche"
                        ? t("ca.type_fiche")
                        : t("ca.type_libre")
                    : `${entree.titre} · ${libelleSection(entree)}`}
                  {entree.epingle ? " ★" : ""}
                </span>
                {/* La case à cocher au crayon : « je la sais ». */}
                <span aria-hidden="true" className="mt-0.5 inline-block size-[3.2mm] shrink-0 border border-black" />
              </div>
              {entree.citation && (
                <div className="mt-1 border-l border-black pl-2">
                  <NoteTexte texte={entree.citation} className="text-[9.5pt] italic leading-[1.35] text-neutral-800" />
                </div>
              )}
              {entree.note && <NoteTexte texte={entree.note} className="mt-1 text-[10pt] leading-[1.38]" />}
              {entree.genre === "libre" && entree.a_image && (
                <div className="mt-1.5 [&_button]:border-0 [&_button]:bg-transparent">
                  <ImageNote noteId={entree.id} version={entree.updated_at ?? undefined} className="max-h-[70mm] w-auto max-w-full object-contain" />
                </div>
              )}
            </li>
          )
        })}
      </ol>

      <p className="mt-2 flex items-center justify-between font-sans text-[7.5pt] text-neutral-600">
        <span>{t("imp.case")}</span>
        <span>{t("imp.pied", { site: SITE_NAME })}</span>
      </p>
    </div>
  )
}
