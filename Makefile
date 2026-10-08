# Raccourcis (Linux, macOS). Sous Windows, utiliser directement : python taches.py <tâche>
.PHONY: installer donnees tests fiche duel grille bannieres video controle tout
installer donnees tests fiche duel grille bannieres video tout:
	python taches.py $@
controle:
	python taches.py video --controle
