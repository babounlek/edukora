import type { FicheEdukora } from "@/api/types"
import { NoteTexte } from "@/components/NoteTexte"
import { SITE_NAME } from "@/lib/site"
import { localeCourante, t, tn, useI18n } from "@/lib/i18n"

/** « Tombé en 2018, 2019 · Examen blanc : 2021 » : sur papier, toutes les années, rien à déplier. */
function annees(fiche: FicheEdukora): string {
  const officielles = fiche.sessions.filter((s) => s.origine === "OFFICIEL").map((s) => s.annee).sort((a, b) => a - b)
  const blancs = [...new Set(fiche.sessions.filter((s) => s.origine !== "OFFICIEL").map((s) => s.annee))]
  return [
    officielles.length ? `${tn("fe.tombe", officielles.length)} ${officielles.join(", ")}` : "",
    blancs.length ? t("fe.blanc", { annees: blancs.join(", ") }) : "",
  ]
    .filter(Boolean)
    .join(" · ")
}

/**
 * La feuille qui sort de l'imprimante depuis « Fiches EduKora ». Comme celle des notes (voir notes/NotesImprimees) : A4,
 * noir sur blanc, deux colonnes serrées, une fiche non coupée. Les réponses des « À toi » sont regroupées à la fin, pour
 * que l'élève cherche avant de lire. Les fiches verrouillées ne sortent pas : le papier n'aurait que leur titre.
 */
export function FichesImprimees({ titre, fiches }: { titre: string; fiches: FicheEdukora[] }) {
  useI18n()
  const lisibles = fiches.filter((f) => !f.verrouillee)
  if (lisibles.length === 0) return null
  const date = new Date().toLocaleDateString(localeCourante(), { day: "numeric", month: "long", year: "numeric" })
  const reponses = lisibles
    .map((fiche, i) => ({ fiche, numero: i + 1 }))
    .filter(({ fiche }) => fiche.exercice && fiche.reponse)
  return (
    <div className="feuille-imprimee hidden text-black print:block">
      {/* Posé ici, le format ne vaut que tant que la feuille existe. Pas de page CSS nommée (voir NotesImprimees). */}
      <style>{"@page { size: A4; margin: 12mm 11mm 13mm; }"}</style>
      <div className="flex items-end justify-between gap-6 border-b-2 border-black pb-2">
        <div className="min-w-0">
          <p className="font-sans text-[8pt] font-semibold uppercase tracking-[0.2em]">{t("fe.titre")}</p>
          <p className="font-display text-[20pt] font-semibold leading-tight">{titre}</p>
        </div>
        <div className="shrink-0 text-right font-sans text-[8.5pt] leading-snug">
          <p>
            {tn("fe.nombre", lisibles.length)} · {date}
          </p>
        </div>
      </div>

      <ol className="mt-3 list-none columns-2 gap-[9mm] p-0 [column-rule:0.5pt_solid_#bbb]">
        {lisibles.map((fiche, i) => (
          <li key={fiche.id} className="mb-[3mm] break-inside-avoid border-b border-neutral-400 pb-[3mm] text-[10pt] leading-[1.38]">
            <p className="break-after-avoid font-display text-[11.5pt] font-semibold leading-tight">
              {i + 1}. {fiche.terme}
              {fiche.a_relire ? ` (${t("fe.a_relire")})` : ""}
            </p>
            <p className="mt-0.5 font-sans text-[7.5pt] text-neutral-700">
              {[fiche.rubrique, annees(fiche)].filter(Boolean).join(" · ")}
            </p>
            <NoteTexte texte={fiche.definition ?? ""} className="mt-1 text-[10pt] leading-[1.38]" />
            {fiche.exemple && (
              <div className="mt-1.5 border-l border-neutral-500 pl-2">
                <NoteTexte texte={fiche.exemple} className="text-[9.5pt] leading-[1.35]" />
              </div>
            )}
            {fiche.piege && (
              <div className="mt-1.5 border-l-2 border-black pl-2">
                <p className="font-sans text-[7.5pt] font-bold uppercase tracking-wide">{t("fe.piege")}</p>
                <NoteTexte texte={fiche.piege} className="text-[9.5pt] leading-[1.35]" />
              </div>
            )}
            {fiche.exercice && (
              <div className="mt-1.5 border border-dashed border-neutral-600 px-2 py-1">
                <p className="font-sans text-[7.5pt] font-bold uppercase tracking-wide">{t("fe.a_toi")}</p>
                <NoteTexte texte={fiche.exercice} className="text-[9.5pt] leading-[1.35]" />
              </div>
            )}
          </li>
        ))}
      </ol>

      {reponses.length > 0 && (
        <section className="mt-3 border-t-2 border-black pt-2">
          <p className="break-after-avoid font-sans text-[8pt] font-semibold uppercase tracking-[0.2em]">{t("fe.imp_reponses")}</p>
          <ul className="mt-2 list-none columns-2 gap-[9mm] p-0 [column-rule:0.5pt_solid_#bbb]">
            {reponses.map(({ fiche, numero }) => (
              <li key={fiche.id} className="mb-[2mm] flex break-inside-avoid items-baseline gap-1.5">
                <span className="font-sans text-[8.5pt] font-bold tabular-nums">{numero}.</span>
                <NoteTexte texte={fiche.reponse ?? ""} className="min-w-0 flex-1 text-[9.5pt] leading-[1.35]" />
              </li>
            ))}
          </ul>
        </section>
      )}

      <p className="mt-2 text-right font-sans text-[7.5pt] text-neutral-600">{t("imp.pied", { site: SITE_NAME })}</p>
    </div>
  )
}
