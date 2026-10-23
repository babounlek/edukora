import { cn } from "@/lib/utils"

/**
 * Le personnage-guide : un livre ouvert, au trait, dans la couleur du texte courant
 * (`currentColor`, donc le vert d'EduKora en clair comme en sombre, sans nouvelle teinte).
 * Un seul tracé, moins d'un kilo-octet, sans image à télécharger et sans animation.
 * Décoratif : le titre de la carte dit déjà tout, d'où `aria-hidden`.
 */
export function LivreOuvert({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
      className={cn("size-6 shrink-0", className)}
    >
      <path d="M12 6.5C10.4 5.3 8.2 4.75 5.5 4.75c-.9 0-1.75.07-2.5.2v13.3c.75-.13 1.6-.2 2.5-.2 2.7 0 4.9.55 6.5 1.75 1.6-1.2 3.8-1.75 6.5-1.75.9 0 1.75.07 2.5.2V4.95c-.75-.13-1.6-.2-2.5-.2-2.7 0-4.9.55-6.5 1.75Z" />
      <path d="M12 6.5v13.25" />
    </svg>
  )
}
