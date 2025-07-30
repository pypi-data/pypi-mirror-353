from pathlib import Path

import httpx
import logfire
import rich
from loguru import logger

from stadt_bonn_oparl.api.models import Consultation
from stadt_bonn_oparl.config import OPARL_BASE_URL
from stadt_bonn_oparl.models import OParlAgendaItem, OParlFile
from stadt_bonn_oparl.tasks.files import download_oparl_file


def print_agenda_item(
    agenda_item: OParlAgendaItem, data_path: Path, http_client: httpx.Client
):
    """
    Print the details of an agenda item, including its consultation and files.

    Args:
        agenda_item (AgendaItemResponse): The agenda item to print.
        data_path (Path): The path to the directory where files will be downloaded.
        http_client (httpx.Client): The HTTP client to use for API requests.
    """

    if agenda_item.consultation:
        cid = httpx.URL(agenda_item.consultation).params.get("id")
        bi = httpx.URL(agenda_item.consultation).params.get("bi")

        c = http_client.get(f"{OPARL_BASE_URL}/consultations/?id={cid}&bi={bi}")
        if c.status_code != 200:
            rich.print(f"[red]Error fetching consultation {cid}[/red]")

        logger.debug(f"Fetched consultation {cid} for agenda item {agenda_item.id}")
        logger.debug(f"Consultation data: {c.json()}")
        consultation = Consultation.model_validate_json(c.text)

        rich.print(
            f"\t[green]beratene Durcksache:[/green] {consultation.paper_ref} (ID: {consultation.id})"
        )

    # if available, print all the files (only if they have an accessUrl) associated with the agenda item
    if agenda_item.resolutionFile:
        _resolution_oparl_file = OParlFile(**agenda_item.resolutionFile)
        if agenda_item.resolutionFile.get("accessUrl"):
            rich.print(
                f"\t[green]Beschluss:[/green] {agenda_item.resolutionFile['accessUrl']}"
            )
            rich.print(
                download_oparl_file.delay(
                    str(data_path),
                    _resolution_oparl_file.model_dump_json(),
                )
            )

    if agenda_item.auxiliaryFile:
        for aux_file in agenda_item.auxiliaryFile:
            _aux_file_oparl_file = OParlFile(**aux_file)
            if aux_file.get("accessUrl"):
                rich.print(f"\t[green]Zusatzdokument:[/green] {aux_file['accessUrl']}")
                rich.print(
                    download_oparl_file.delay(
                        str(data_path),
                        _aux_file_oparl_file.model_dump_json(),
                    )
                )


def print_participant(participant: str, http_client: httpx.Client):
    """
    Print the details of a participant.

    Args:
        participant (str): The URL of the participant.
        http_client (httpx.Client): The HTTP client to use for API requests.
    """
    with logfire.span(
        "Fetching participant information from OParl Cache",
        participant=participant,
    ):
        p_id = httpx.URL(participant).params.get("id")
        response = http_client.get(f"{OPARL_BASE_URL}/persons/?id={p_id}")
        if response.status_code != 200:
            rich.print(f"[red]Error fetching participant {p_id}[/red]")
            return
        person = response.json()

    if not person:
        rich.print(f"[red]Participant {p_id} not found.[/red]")
        return

    affix = ""
    if person.get("affix"):
        affix = f", ({person['affix']})"
    rich.print(
        f"\t[green]{person['name']} ({person['id']}){affix}[/green] - {person.get('role', 'keine Rolle in dieser Sitzung')}"
    )
