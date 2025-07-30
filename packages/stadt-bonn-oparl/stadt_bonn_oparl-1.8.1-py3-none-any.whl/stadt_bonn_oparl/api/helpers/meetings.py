import httpx
import logfire
from chromadb import Collection
from fastapi import HTTPException

from stadt_bonn_oparl.api.config import UPSTREAM_API_URL
from stadt_bonn_oparl.api.helpers.processors import _process_meeting
from stadt_bonn_oparl.api.models import MeetingListResponse, MeetingResponse
from stadt_bonn_oparl.models import OrganizationType


async def _get_meeting_by_id(
    http_client: httpx.Client, meeting_id: int
) -> MeetingResponse:
    """Helper function to get a meeting by ID from the OParl API."""
    _url = UPSTREAM_API_URL + f"/meetings?id={meeting_id}"

    # TODO: retry on timeut or connection errors
    response = http_client.get(_url, timeout=30.0)
    if response.status_code == 200:
        _json = response.json()

        # check if the object has deleted = True aka not found
        if _json.get("deleted", False):
            raise HTTPException(
                status_code=404,
                detail=f"Meeting with ID {meeting_id} not found in OParl API",
            )

        _process_meeting(_json)
        return MeetingResponse(**_json)

    raise HTTPException(
        status_code=500,
        detail=f"Failed to fetch meeting with ID {meeting_id} from OParl API",
    )


async def _get_meetings_by_organization_id(
    http_client: httpx.Client,
    collection: Collection | None,
    organization_id: int,
    organization_type: OrganizationType = OrganizationType.gr,
) -> tuple[bool, MeetingListResponse]:
    """Helper function to get meetings by organization ID from the OParl API.
    If the meetings are already in the ChromaDB collection, it will return them from there.
    If not, it will fetch them from the OParl API and upsert them into the collection.

    Parameters
    ----------
    http_client : httpx.Client
        The HTTP client to use for making requests.
    collection : Collection | None
        The ChromaDB collection to use for caching meetings.
    organization_id : int
        The ID of the organization to fetch meetings for.
    organization_type : OrganizationType, optional
        The type of the organization (default is OrganizationType.gr).

    Returns
    -------
    tuple[bool, MeetingListResponse]
        A tuple containing a boolean indicating if the meetings were fetched freshly from the OParl API,
        and a MeetingListResponse containing the meetings.
    """
    _url = f"{UPSTREAM_API_URL}/meetings?organization={organization_id}&typ={organization_type.name}"

    if collection is not None:
        with logfire.span(
            "Checking ChromaDB for meetings", organization_id=organization_id
        ):
            # TODO
            pass

    with logfire.span(
        "Fetching meetings from OParl API", organization_id=organization_id
    ):
        # TODO implement pagination
        response = http_client.get(_url, timeout=120.0)
        if response.status_code == 200:
            _json = response.json()

            for meeting in _json["data"]:
                _process_meeting(meeting)

            return True, MeetingListResponse(**_json)

        elif response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"No meetings found for organization ID {organization_id}",
            )
    raise HTTPException(
        status_code=500,
        detail=f"Failed to fetch meetings with organization ID {organization_id} from OParl API",
    )
