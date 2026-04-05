"""HubSpot CRM integration — bidirectional sync for leads and deals."""
import logging
from typing import Optional
import hubspot
from hubspot.crm.contacts import SimplePublicObjectInput, ApiException
from hubspot.crm.deals import SimplePublicObjectInput as DealInput
from app.config import settings

logger = logging.getLogger(__name__)

# HubSpot pipeline stage IDs (configure these in your HubSpot portal)
STAGE_MAP = {
    "new_lead": "appointmentscheduled",
    "contact_initiated": "qualifiedtobuy",
    "response_received": "presentationscheduled",
    "qualified": "decisionmakerboughtin",
    "docs_requested": "contractsent",
    "docs_received": "closedwon",
    "under_verification": "closedwon",
    "approved": "closedwon",
    "visit_scheduled": "closedwon",
    "closed_won": "closedwon",
    "closed_lost": "closedlost",
}


class HubSpotService:
    def __init__(self):
        self._client = hubspot.Client.create(access_token=settings.hubspot_api_key)

    def create_or_update_contact(self, lead) -> Optional[str]:
        """
        Create or update a HubSpot contact from a Lead model.
        Returns HubSpot contact ID.
        """
        properties = {
            "firstname": lead.owner_name.split()[0] if lead.owner_name else "",
            "lastname": " ".join(lead.owner_name.split()[1:]) if lead.owner_name and len(lead.owner_name.split()) > 1 else "",
            "phone": lead.phone or "",
            "email": lead.email or "",
            "mobilephone": lead.whatsapp or "",
            "hs_lead_status": STAGE_MAP.get(lead.pipeline_stage.value, "NEW"),
            "lead_score": str(lead.lead_score),
            "notes_last_contacted": lead.notes or "",
        }

        try:
            if lead.hubspot_contact_id:
                # Update existing contact
                self._client.crm.contacts.basic_api.update(
                    contact_id=lead.hubspot_contact_id,
                    simple_public_object_input=SimplePublicObjectInput(properties=properties),
                )
                logger.info(f"HubSpot contact updated: {lead.hubspot_contact_id}")
                return lead.hubspot_contact_id
            else:
                # Create new contact
                response = self._client.crm.contacts.basic_api.create(
                    simple_public_object_input=SimplePublicObjectInput(properties=properties),
                )
                contact_id = response.id
                logger.info(f"HubSpot contact created: {contact_id}")
                return contact_id

        except ApiException as exc:
            logger.error(f"HubSpot contact sync failed: {exc}")
            return None

    def create_deal(self, lead, property_model=None, deal_type: str = "buy") -> Optional[str]:
        """Create a HubSpot deal for an approved lead."""
        prop = property_model or (lead.properties[0] if lead.properties else None)

        deal_properties = {
            "dealname": f"{lead.owner_name} — {prop.locality if prop else 'Delhi NCR'} ({deal_type.upper()})",
            "amount": str(prop.price) if prop and prop.price else "0",
            "dealtype": "newbusiness",
            "pipeline": "default",
            "dealstage": STAGE_MAP.get(lead.pipeline_stage.value, "appointmentscheduled"),
            "closedate": "",
            "description": f"UIG Property {deal_type.upper()} — Lead #{lead.id}",
        }

        try:
            response = self._client.crm.deals.basic_api.create(
                simple_public_object_input=DealInput(properties=deal_properties),
            )
            deal_id = response.id

            # Associate deal with contact
            if lead.hubspot_contact_id:
                self._client.crm.deals.associations_api.create(
                    deal_id=deal_id,
                    to_object_type="contacts",
                    to_object_id=lead.hubspot_contact_id,
                    association_type="deal_to_contact",
                )

            logger.info(f"HubSpot deal created: {deal_id}")
            return deal_id

        except ApiException as exc:
            logger.error(f"HubSpot deal creation failed: {exc}")
            return None

    def update_deal_stage(self, hubspot_deal_id: str, stage: str) -> bool:
        """Update the stage of an existing HubSpot deal."""
        try:
            self._client.crm.deals.basic_api.update(
                deal_id=hubspot_deal_id,
                simple_public_object_input=DealInput(
                    properties={"dealstage": STAGE_MAP.get(stage, stage)}
                ),
            )
            return True
        except ApiException as exc:
            logger.error(f"HubSpot deal stage update failed: {exc}")
            return False
