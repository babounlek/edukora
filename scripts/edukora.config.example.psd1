# Copier en scripts/edukora.config.psd1 (fichier IGNORE par git) puis adapter.
# Aucun mot de passe ici : l'authentification se fait par cle SSH dediee.
@{
    # Interpreteur Python 3.9+ (le "python" nu est le stub du Microsoft Store). Vide = detection auto.
    Python             = ''

    # Git Bash (PAS le bash.exe de WSL qui est dans le PATH).
    GitBash            = 'C:\Program Files\Git\bin\bash.exe'

    Conteneur          = 'edukora-backend-1'

    # Publication en production (phase 5). Laisser vide tant qu'elle n'est pas utilisee.
    Hote               = ''
    Utilisateur        = 'deploy'
    Port               = 22
    CleSsh             = ''   # ex. C:\Users\<vous>\.ssh\edukora_deploy_ed25519 (cle DEDIEE, jamais celle du poste)
    KnownHosts         = ''   # fichier known_hosts dedie contenant l'empreinte de l'hote (StrictHostKeyChecking=yes)
    CheminServeur      = '/srv/edukora'
    DossierLotsServeur = '/srv/edukora-lots'

    # Reglages avances (valeurs par defaut raisonnables ; ne les changer qu'en connaissance de cause).
    ScriptServeur        = ''     # vide = <CheminServeur>/deploy/sync-lot.sh
    SshExe               = 'ssh'
    ScpExe               = 'scp'
    DelaiSondageSecondes = 5      # intervalle entre deux interrogations de l'etat d'un lot
    DelaiMaxLotSecondes  = 7200   # au-dela : resultat INDETERMINE (code 3), jamais un echec suppose
    ToleranceReseau      = 8      # coupures reseau consecutives tolerees pendant le suivi
}
