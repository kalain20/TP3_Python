import os
from getpass import getpass

from utils import HacheurDeMotDePasse, est_une_adresse_email_valide


class Utilisateur:
    """
    Classe représentant un utilisateur membre de ULFlix.

    Un utilisateur a les attributs suivants:
        - nom (str): le nom de l'utilisateur,
        - email (str): l'adresse email de l'utilisateur,
        - age (int): l'âge de l'utilisateur,
        - pays (str): le pays de l'utilisateur,
        - abonnement (int): l'abonnement de l'utilisateur
            * 1 pour un abonnement régional
            * et 2 pour un abonnement international
        - mot_de_passe (str): la version hachée du mot de passe de l'utilisateur.
    """

    def __init__(self, nom, email, age, pays, abonnement, mot_de_passe):
        self.nom = nom
        self.email = email
        self.mot_de_passe = mot_de_passe
        self.age = int(age)
        self.pays = pays
        self.abonnement = int(abonnement)


class AnnuaireUtilisateur:
    """
    Classe représentant l'annuaire des utilisateurs de ULFlix.

    Un AnnuaireUtilisateur est composé des attributs suivants:
        - chemin_base_de_donnees (str): le chemin menant au fichier dans lequel les informations des utilisateurs sont sauvegardées.
        - utilisateurs (list): la liste des utilisateurs faisant partie de l'annuaire.
    """

    def __init__(self, chemin_base_de_donnees):
        self.chemin_base_de_donnees = chemin_base_de_donnees

        if os.path.exists(self.chemin_base_de_donnees):
            with open(self.chemin_base_de_donnees, encoding="utf-8") as fichier:
                lignes = [ligne.strip() for ligne in fichier]
        else:
            lignes = []

        self.utilisateurs = [Utilisateur(*ligne.split(",")) for ligne in lignes]

    def inscrire(self):
        """
        Méthode permettant de récupérer les informations de l'utilisateur
        afin de lui créer un compte ULFlix.

        Returns:
            Utilisateur: Un objet de la classe Utilisateur avec les attributs
            (nom, email, age, pays, abonnement, mot_de_passe) remplis.
        """
        nom = None
        while nom is None:
            nom = input("Veuillez entrer votre nom: ").lower()
            if len(nom) == 0 or nom.isspace():
                print("Le nom ne peut pas être vide.")
                nom = None

        adresses_emails_existantes = set([u.email for u in self.utilisateurs])
        email = None
        while email is None:
            email = input("Veuillez entrer votre email: ").lower()

            if not est_une_adresse_email_valide(email):
                print("L'adresse email entrée est invalide.")
                email = None

            if email in adresses_emails_existantes:
                print(
                    "Un utilisateur est déjà inscrit avec cette adresse email. "
                    "Veuillez vous connecter si vous êtes cet utilisateur ou utilisez une autre adresse email."
                )
                email = None

        age = None
        while age is None:
            try:
                age = int(input("Veuillez entrer votre âge: "))
                assert age >= 0
            except (ValueError, AssertionError):
                print("L'âge doit être un entier positif.")
                age = None

        pays = None
        while pays is None:
            pays = input("Veuillez entrer votre pays: ").lower()
            if len(pays) == 0 or pays.isspace():
                print("Vous devez entrer un pays valide.")
                pays = None

        abonnement = None
        while abonnement is None:
            try:
                abonnement = int(input("Veuillez entrer votre type d'abonnement - 1 [régional] ou 2 [international]: "))
                assert abonnement in [1, 2]
            except (ValueError, AssertionError):
                print("Le type d'abonement doit être 1 pour régional ou 2 pour international.")
                abonnement = None

        mot_de_passe = None
        while mot_de_passe is None:
            mot_de_passe = input("Veuillez entrer votre mot de passe (min 6 caractères): ")
            if len(mot_de_passe) < 6 or mot_de_passe.isspace():
                print("Le mot de passe doit faire au minimum 6 caractères.")
                mot_de_passe = None

        hash_mot_de_passe = HacheurDeMotDePasse.hacher(mot_de_passe)

        utilisateur = Utilisateur(
            nom=nom,
            email=email,
            age=age,
            pays=pays,
            abonnement=abonnement,
            mot_de_passe=hash_mot_de_passe,
        )

        with open(self.chemin_base_de_donnees, mode="a", encoding="utf-8") as fichier:
            fichier.write(",".join([nom, email, str(age), pays, str(abonnement), hash_mot_de_passe]) + "\n")

        return utilisateur

    def authentifier(self):
        """
        Méthode permettant d'authentifier un utilisateur faisant partie
        des utilisateurs membres ULFlix.

        Cette méthode demande premièrement à l'utilisateur d'entrer son adresse email (celle utilisée lors de l'inscription), s'assure par la suite qu'il s'agisse bel et bien d'une adresse email valide (vous devez vous servir de la fonction est_une_adresse_email_valide afin de vérifier si oui ou non l'adresse email entrée par l'utilisateur est une adresse email valide). S'il ne s'agit pas d'une adresse email valide, il faudra afficher le message "L'adresse email entrée est invalide." et redemander à l'utilisateur son adresse email.

        La méthode vérifie ensuite que l'adresse email entrée par l'utilisateur (qui est censée être valide si vous êtes rendu à cette étape) correspond à l'adresse email de l'un des utilisateurs présents au niveau de la base de données. Si ce n'est pas le cas, il faudra afficher le message "Nous n'avons trouvé aucun utilisateur avec cette adresse email au niveau de notre système." et redemander à l'utilisateur son adresse email.

        Si l'adresse email entrée par l'utilisateur est valide et qu'elle correspond bel et bien à l'adresse email de l'un des utilisateurs présents au niveau de la base de données, la méthode devra ensuite demander à l'utilisateur d'entrer son mot de passe. Si le mot de passe entré par l'utilisateur n'est pas le bon, il faudra afficher le message "Mot de passe incorrect." et redemander à l'utilisateur son mot de passe. Si le mot de passe entré par l'utilisateur s'avère par contre être le bon, la méthode devra retrouver l'utilisateur correspondant à la combinaison email/mot de passe entrée.

        Vous allez devoir utiliser la méthode de classe HacheurDeMotDePasse.verifier(...) afin de vérifier si le mot de passe entré par l'utilisateur est correct.

        Returns:
            Utilisateur: Un objet de la classe Utilisateur représentant
            l'utilisateur venant d'être authentifié.
        """
        email = None
        while email is None:
            email = input("Veuillez entrer votre email: ").lower()
            if not est_une_adresse_email_valide(email):
                print("L'adresse email entrée est invalide.")
                email = None

            mot_de_passe_clair = None
            while mot_de_passe_clair is None:
                mot_de_passe_clair = input("Veuillez entrer votre mot de passe (min 6 caractères): ")
                if len(mot_de_passe_clair) < 6 or mot_de_passe_clair.isspace():
                    print("Le mot de passe doit faire au minimum 6 caractères.")
                    mot_de_passe_clair = None

            adresses_emails_existantes = set([u.email for u in self.utilisateurs])

            for utilisateur in self.utilisateurs:
                verifie = HacheurDeMotDePasse.verifier(utilisateur.mot_de_passe, mot_de_passe_clair)

                if email in adresses_emails_existantes and verifie:
                    un_utilisateur = Utilisateur(
                        nom=utilisateur.nom,
                        email=utilisateur.email,
                        age=utilisateur.age,
                        pays=utilisateur.pays,
                        abonnement=utilisateur.abonnement,
                        mot_de_passe=utilisateur.mot_de_passe
                    )
                    return un_utilisateur


        # À Compléter
