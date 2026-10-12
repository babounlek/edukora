/**
 * Saisie d'un numéro camerounais dans un champ « 9 chiffres ». L'API attend toujours ces
 * 9 chiffres locaux (ex. 677123456), jamais le format international : cette fonction
 * ramène donc ce que l'élève tape ou colle à ce format-là.
 *
 * Un `maxLength={9}` sur le champ tronquait un collage « +237 677 12 34 56 » (ou depuis
 * les contacts : « 00237… ») à ses 9 premiers caractères, soit « +237 677 » - le numéro
 * ressortait faux sans qu'aucune erreur ne s'affiche. On filtre donc ici, à la saisie.
 */
export function chiffresNumeroLocal(saisie: string): string {
  let chiffres = saisie.replace(/\D/g, "")
  // Le préfixe n'est retiré que s'il est suivi d'un numéro complet (9 chiffres) : un
  // numéro local en cours de frappe peut très bien commencer par « 237 » sans être
  // un indicatif (ex. 237 000 000), et on ne doit pas le manger caractère par caractère.
  for (const prefixe of ["00237", "237"]) {
    if (chiffres.startsWith(prefixe) && chiffres.length - prefixe.length >= 9) {
      chiffres = chiffres.slice(prefixe.length)
      break
    }
  }
  return chiffres.slice(0, 9)
}
