# Abes_Apis_Interface 
Interfaces d'appel et de traitement des réponses des APIS du SUDOC
## AbesXml
[Permet de travailler avec l'api du SUDOC qui retourne une notice en XML. Prend un PPN en paramètre](./AbesXml.py)
### Get_etat_col
Pour un RCR donné retourne la liste des Etats de collection formatés (955$$r du SUDOC)
## [Bacon_id2Kabart](./Bacon_Id2Kabart.py)
A set of function wich handle data returned by service ['Bacon in json'](http://documentation.abes.fr/aidebacon/index.html#WebserviceId2)
On init take a bib identifier in argument (ISBN or ISSN)


