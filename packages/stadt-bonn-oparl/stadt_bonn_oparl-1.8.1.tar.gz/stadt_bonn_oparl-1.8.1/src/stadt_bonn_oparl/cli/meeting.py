import uuid

import chromadb
import httpx
import rich
from chromadb.config import Settings
from cyclopts import App
from loguru import logger
from pydantic import DirectoryPath

from stadt_bonn_oparl.api.helpers.meetings import _get_meeting_by_id
from stadt_bonn_oparl.api.models import MeetingResponse
from stadt_bonn_oparl.cli.helpers import print_agenda_item, print_participant
from stadt_bonn_oparl.config import OPARL_BASE_URL, UPSTREAM_API_URL
from stadt_bonn_oparl.tasks.files import download_oparl_file

meeting = App(name="meeting", help="work with OParl meetings present in VectorDB")


@meeting.command()
async def get(data_path: DirectoryPath, meeting_id: int):
    """
    Query the VectorDB for a specific Meeting by its ID and get/print it.

    Parameters
    ----------
    data_path: DirectoryPath
        Path to the directory where OParl data will be saved.
    meeting_id: int
        The ID of the meeting to query.
    """
    result: MeetingResponse | None = None
    http_client = httpx.Client(base_url=OPARL_BASE_URL)
    chromadb_client = chromadb.PersistentClient(
        path="./chroma-api",
        settings=Settings(
            anonymized_telemetry=False,  # disable posthog telemetry
        ),
    )

    collection = chromadb_client.get_collection(name="meetings")

    logger.debug(f"Searching for Sitzung {meeting_id}")

    # first, let's see if we got the meeting in our local VectorDB
    meeting_id_ref = str(
        uuid.uuid5(uuid.NAMESPACE_URL, f"{UPSTREAM_API_URL}/meetings?id={meeting_id}")
    )
    _results = collection.get(
        ids=[meeting_id_ref]
    )  # TODO: we need to get the Consultation embedded data like meeting and paper loaded in the background

    if _results and _results["documents"]:
        logger.debug(f"Meeting {meeting_id} found in VectorDB.")
        result = MeetingResponse.model_validate_json(_results["documents"][0])
    else:
        # first, let's get the meeting by its ID from the rest API
        result = await _get_meeting_by_id(
            meeting_id=meeting_id,
            http_client=http_client,
        )
        if not result:
            logger.warning(f"Metting with ID {meeting_id} not found.]")
            return

        logger.debug(f"Meeting {meeting_id} found via API.")

    # print some meeting details
    rich.print(
        f"[green]Sitzung:[/green] {result.name} (ID: {result.id}) - {result.start}"
    )
    rich.print(f"[green]Status:[/green] {result.meetingState}")

    # let's download the invitation file if it exists
    if result.invitation:
        rich.print(
            f"Einladung: [green]verfügbar unter:[/green] {result.invitation.accessUrl}"
        )
        rich.print(
            download_oparl_file.delay(
                str(data_path), result.invitation.model_dump_json()
            )
        )

    for agenda_item in result.agendaItem:
        if agenda_item.name != "(nichtöffentlich)":
            rich.print(f"TOP: {agenda_item.name} (ID: {agenda_item.id})")

            print_agenda_item(
                agenda_item=agenda_item,
                data_path=data_path,
                http_client=http_client,
            )
    if result.verbatimProtocol:
        rich.print(
            f"Sitzung:\n\t[green]Verbatim protocol available:[/green] {result.verbatimProtocol.accessUrl}"
        )
        download_oparl_file.delay(
            str(data_path),
            result.verbatimProtocol.model_dump_json(),
        )

    # let's print all the participants
    if result.participant_ref:
        rich.print("Teilnehmende:")
        for participant in result.participant_ref:
            print_participant(
                participant=participant,
                http_client=http_client,
            )
