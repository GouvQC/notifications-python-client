import logging
import re

from notifications_python_client.base import BaseAPIClient

logger = logging.getLogger(__name__)


class NotificationsAPIClient(BaseAPIClient):
    def send_sms_notification(
        self, phone_number, template_id, personalisation=None, reference=None, sms_sender_id=None
    ):
        """
        Envoie d'une notification de type SMS.
        :param phone_number: Numéro de téléphone du destinataire.
        :param template_id: ID du gabarit utilisé pour le SMS.
        :param personalisation: (optionnel) Données de personnalisation pour le gabarit.
        :param reference: (optionnel) Référence unique pour identifier la notification.
        :param sms_sender_id: (optionnel) ID de l'expéditeur du SMS.
        :return: Résultat de l'appel API POST.
        """
        notification = {
            "phone_number": phone_number,
            "template_id": template_id,
            **({"personalisation": personalisation} if personalisation else {}),
            **({"reference": reference} if reference else {}),
            **({"sms_sender_id": sms_sender_id} if sms_sender_id else {}),
        }
        return self.post("/v2/notifications/sms", data=notification)

    def send_email_notification(
        self,
        email_address,
        template_id,
        personalisation=None,
        reference=None,
        email_reply_to_id=None,
        scheduled_for=None,
        importance=None,
        cc_address=None,
    ):
        """
        Envoie d'une notification de type email.
        :param email_address: Adresse email du destinataire.
        :param template_id: ID du gabarit utilisé pour l'email.
        :param personalisation: (optionnel) Données de personnalisation pour le gabarit.
        :param reference: (optionnel) Référence unique pour identifier la notification.
        :param email_reply_to_id: (optionnel) ID de l'adresse de réponse pour l'email.
        :param scheduled_for: (optionnel) Date d'envoi programmé.
        :param importance: (optionnel) Niveau d'importance ("high", "normal", "low").
        :param cc_address: (optionnel) L'adresse courriel en copie.
        :return: Résultat de l'appel API POST.
        """

        if importance and importance not in ["high", "normal", "low"]:
            raise ValueError("importance doit être: high, normal ou low")

        notification = {"email_address": email_address, "template_id": template_id}

        if personalisation:
            notification.update({"personalisation": personalisation})
        if reference:
            notification.update({"reference": reference})
        if email_reply_to_id:
            notification.update({"email_reply_to_id": email_reply_to_id})
        if scheduled_for:
            notification.update({"scheduled_for": scheduled_for})
        if importance:
            notification.update({"importance": importance})
        if cc_address:
            notification.update({"cc_address": cc_address})

        return self.post("/v2/notifications/email", data=notification)

    def send_bulk_notifications(
        self, template_id, name, rows=None, csv=None, reference=None, scheduled_for=None, reply_to_id=None
    ):
        """
        Envoie de notifications en masse.
        :param template_id: ID du gabarit utilisé pour les notifications.
        :param name: Nom de l'envoi en masse.
        :param rows: (optionnel) Liste des lignes de données pour les notifications.
                     La première ligne doit contenir les en-têtes.
        :param csv: (optionnel) Données CSV encodées en base64.
        :param reference: (optionnel) Référence unique pour identifier l'envoi en masse.
        :param scheduled_for: (optionnel) Date et heure de planification de l'envoi (format ISO 8601).
        :param reply_to_id: (optionnel) ID de l'adresse de réponse.
        :return: Résultat de l'appel API POST.
        """
        if not rows and not csv:
            raise ValueError("Vous devez fournir soit 'rows', soit 'csv'.")
        if rows and csv:
            raise ValueError("Vous ne pouvez pas fournir à la fois 'rows' et 'csv'.")

        data = {
            "template_id": template_id,
            "name": name,
            **({"rows": rows} if rows else {}),
            **({"csv": csv} if csv else {}),
            **({"reference": reference} if reference else {}),
            **({"scheduled_for": scheduled_for} if scheduled_for else {}),
            **({"reply_to_id": reply_to_id} if reply_to_id else {}),
        }

        return self.post("/v2/notifications/bulk", data=data)

    def get_notification_by_id(self, id):
        """
        Récupère les détails d'une notification spécifique par son ID.
        :param id: ID de la notification.
        :return: Détails de la notification.
        """
        return self.get(f"/v2/notifications/{id}")

    def get_all_notifications(self, status=None, template_type=None, reference=None, older_than=None):
        """
        Récupère toutes les notifications avec des filtres optionnels.
        :param status: Filtrer par statut de notification.
        :param template_type: Filtrer par type de gabarit ('email', 'sms').
        :param reference: Filtrer par référence unique.
        :param older_than: Récupérer les notifications plus anciennes qu'un ID donné.
        :param include_jobs: Inclure les notifications liées aux jobs.
        :return: Liste des notifications.
        """
        params = {}
        if status:
            params["status"] = status
        if template_type:
            params["template_type"] = template_type
        if reference:
            params["reference"] = reference
        if older_than:
            params["older_than"] = older_than

        return self.get("/v2/notifications", params=params)

    def get_all_notifications_iterator(self, status=None, template_type=None, reference=None, older_than=None):
        """
        Itère sur toutes les notifications en paginant automatiquement.
        :param status: Filtrer par statut de notification.
        :param template_type: Filtrer par type de gabarit ('email', 'sms').
        :param reference: Filtrer par référence unique.
        :param older_than: Récupérer les notifications plus anciennes qu'un ID donné.
        :yield: Une notification à la fois.
        """
        result = self.get_all_notifications(status, template_type, reference, older_than)
        notifications = result.get("notifications")
        while notifications:
            yield from notifications
            next_link = result["links"].get("next")
            notification_id = re.search("[0-F]{8}-[0-F]{4}-[0-F]{4}-[0-F]{4}-[0-F]{12}", next_link, re.I).group(0)
            result = self.get_all_notifications(status, template_type, reference, notification_id)
            notifications = result.get("notifications")

    def post_template_preview(self, template_id, personalisation):
        """
        Génère un aperçu d'un gabarit avec des données de personnalisation.
        :param template_id: L'ID du gabarit.
        :param personalisation: Données de personnalisation pour le gabarit.
        :return: Aperçu du gabarit.
        """
        template = {"personalisation": personalisation}
        return self.post(f"/v2/template/{template_id}/preview", data=template)

    def get_template(self, template_id):
        """
        Récupère les détails d'un gabarit spécifique.
        :param template_id: L'ID du gabarit.
        :return: Détails du gabarit.
        """
        return self.get(f"/v2/template/{template_id}")

    def get_template_version(self, template_id, version):
        """
        Récupère une version spécifique d'un gabarit.
        :param template_id: L'ID du gabarit.
        :param version: La version spécifique du gabarit.
        :return: Détails de la version du gabarit.
        """
        return self.get(f"/v2/template/{template_id}/version/{version}")

    def get_all_templates(self, template_type=None):
        """
        Récupère tous les gabarits disponibles pour un service.
        :param template_type: (optionnel) Filtrer par type de gabarit ('email', 'sms').
        :return: Liste des gabarits.
        """
        params = {}
        if template_type:
            params["type"] = template_type

        return self.get("/v2/templates", params=params)

    def check_health(self):
        """
        Vérifie l'état de santé du service.
        :return: Réponse JSON contenant le statut de santé.
        """
        return self.get("/health")
