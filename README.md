File Management — Infrastructure AWS 3-Tier
Application web de gestion de fichiers (upload, téléchargement, renommage, suppression) déployée sur une architecture AWS à trois niveaux, entièrement automatisée avec Terraform, Ansible et Jenkins.
Dépôt : github.com/amelachio/file-upload-aws-devops-terraform-ansible-jenkins
Architecture
Afficher l'image
Le projet repose sur un VPC (10.0.0.0/16) découpé en trois sous-réseaux :
•	Un sous-réseau public contenant le frontend, le serveur Ansible (bastion) et Jenkins
•	Un sous-réseau privé pour le backend
•	Un sous-réseau privé pour la base de données
Les sous-réseaux privés n'ont aucune exposition directe à internet. L'accès administratif se fait via le serveur Ansible, qui agit comme point d'entrée unique vers le backend et la base de données. Un NAT Gateway donne un accès sortant à ces deux sous-réseaux pour les mises à jour système.
Le flux applicatif est simple : l'utilisateur passe par CloudFront pour atteindre le frontend ; le frontend relaie les requêtes au backend ; le backend stocke les fichiers dans S3 et leurs métadonnées dans MariaDB.
Stack technique
•	Infrastructure : Terraform
•	Configuration des serveurs : Ansible, avec Ansible Vault pour les secrets
•	Intégration continue : Jenkins
•	Backend et frontend : Python (Flask, Gunicorn), derrière Nginx
•	Base de données : MariaDB
•	Stockage : S3, servi via CloudFront
Sécurité
Le backend accède à S3 via un rôle IAM attaché à l'instance, sans clé d'accès stockée dans le code. Les security groups suivent une logique de liste blanche : le backend et la base de données n'acceptent du trafic que depuis les sources explicitement autorisées, jamais depuis internet directement. L'accès SSH aux trois serveurs administrables (frontend, Ansible, Jenkins) est limité à mon adresse IP. Les identifiants de la base de données sont chiffrés avec Ansible Vault et ne figurent jamais en clair dans le dépôt. Les requêtes SQL utilisent des paramètres liés pour éviter les injections.
Déploiement
L'infrastructure se crée avec Terraform (terraform apply), puis Ansible configure les serveurs (paquets, services, base de données) à partir de l'inventaire et du fichier de secrets. Le code applicatif, lui, est déployé automatiquement par Jenkins à chaque modification poussée sur la branche principale : le pipeline récupère le code depuis GitHub, le copie sur les serveurs concernés par SSH, puis redémarre les services.
Fonctionnalités
Le backend expose une API simple :
•	POST /upload — envoi d'un fichier (image ou PDF)
•	GET /files — liste des fichiers avec leurs métadonnées
•	PUT /files/<id> — renommage
•	DELETE /files/<id> — suppression
Le frontend ajoute une interface pour ces actions, avec téléchargement direct, renommage en un clic et confirmation avant suppression.
Ce que ce projet démontre
Au-delà de la mise en place initiale, ce projet a demandé de résoudre plusieurs problèmes réels une fois l'infrastructure en place : une configuration réseau qui empêchait la base de données d'accepter des connexions distantes, une politique IAM incomplète découverte en testant la suppression de fichiers, et un security group trop permissif qui a fini par attirer des tentatives de connexion SSH automatisées depuis internet, au point de perturber les déploiements. Chacun de ces cas a demandé de diagnostiquer la cause avant de corriger, et de vérifier que la correction tenait dans la durée plutôt que de simplement contourner le symptôme.
Améliorations possibles
•	Ajouter un WAF devant CloudFront
•	Réduire la policy IAM du compte Terraform, actuellement en accès administrateur
•	Passer les secrets vers AWS Secrets Manager
•	Ajouter un certificat HTTPS sur le frontend et le backend
•	Renommer réellement l'objet dans S3 lors d'un renommage, pas seulement son nom affiché
Auteur
Anicet Melachio Ingénieur Infrastructure — Maîtrise en cybersécurité, Université de Sherbrooke
