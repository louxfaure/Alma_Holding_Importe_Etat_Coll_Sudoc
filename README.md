# Import des états de collection dans les holdings Alma
A partir d'une liste de PPN  fournie dans un fichier csv, le programme va récupérer, pour une bibliothèque donnée (ALMA_LIBRARY_ID) et un rcr donné (RCR), la holding dans Alma (via sru Alma) et l'état de collection du SUDOC (vai sudoc.xml).
Pour chaque Holding le programme :
- Backup les 866
- Récupère la 995 $ 5 du SUDOC
- Ecrase la 866$a par l'état de colection du SUDOC
- Ajoute les notes qui étaitent présentent dans la 866 originale