import uuid

import httpx
import logfire
from chromadb import Collection
from fastapi import HTTPException

from stadt_bonn_oparl.api.config import UPSTREAM_API_URL
from stadt_bonn_oparl.api.helpers.processors import _process_person
from stadt_bonn_oparl.api.models import PersonResponse


async def _get_person(
    http_client: httpx.Client, collection: Collection | None, person_id: str
) -> tuple[bool, PersonResponse]:
    """Helper function to get a person by ID from the OParl API."""
    _url = UPSTREAM_API_URL + f"/persons?id={person_id}"

    if collection is not None:
        with logfire.span("Checking ChromaDB for person", person_id=person_id):
            _id_ref = uuid.uuid5(uuid.NAMESPACE_URL, str(_url))
            _doc = collection.get(ids=[str(_id_ref)])
            if _doc and _doc["documents"]:
                # If we have a document, return it
                return False, PersonResponse.model_validate_json(_doc["documents"][0])

    with logfire.span("Fetching person from OParl API", person_id=person_id):
        response = http_client.get(_url, timeout=10.0)

    if response.status_code == 200:
        _json = response.json()

        # check if the person is deleted
        if _json.get("deleted", False):
            raise HTTPException(
                status_code=404,
                detail=f"Person with ID {person_id} not found in OParl API",
            )

        _process_person(_json)
        return True, PersonResponse(**_json)

    raise HTTPException(
        status_code=500,
        detail=f"Failed to fetch person {person_id} information from OParl API",
    )
