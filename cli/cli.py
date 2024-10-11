#!/usr/bin/env python
# Copyright ©, 2024, Lightspark Group, Inc. - All Rights Reserved
# pyre-strict

import asyncio
import json
from datetime import timedelta

import typer
from nostr_sdk import (
    Client,
    EventBuilder,
    Filter,
    Keys,
    Kind,
    Metadata,
    MetadataRecord,
    NostrSigner,
    PublicKey,
)
from typing_extensions import Annotated

app = typer.Typer(
    name="UMA Auth CLI",
    short_help="A CLI helper for managing UMA Auth Client Apps.",
)


@app.command(help="Generate a new nostr keypair.")
def generate_key():
    print("Generating new keypair...")
    keys = Keys.generate()
    nsec = keys.secret_key()
    npub = keys.public_key()
    print(nsec.to_bech32())
    print(npub.to_bech32())
    print(f"nsec hex: {nsec.to_hex()}")
    print(f"npub hex: {npub.to_hex()}")


@app.command(help="Publish client app identity events to the given relays.")
def publish(
    nsec: Annotated[
        str,
        typer.Option(
            "--nsec",
            "-s",
            help="Secret key to sign the event with. Can be hex or bech32.",
            prompt=True,
        ),
    ],
    relays: Annotated[
        list[str],
        typer.Option(
            "--relay",
            "-r",
            help="Relay to publish to.",
        ),
    ],
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name of the client app.",
            prompt=True,
        ),
    ],
    image: Annotated[
        str,
        typer.Option(
            "--image",
            "-i",
            help="URL of the client app image.",
            prompt=True,
        ),
    ],
    nip05: Annotated[
        str,
        typer.Option(
            "--nip05",
            "-5",
            help="NIP-05 address of the client app.",
            prompt=True,
        ),
    ],
    redirect_uris: Annotated[
        list[str],
        typer.Option(
            "--redirect-uri",
            "-u",
            help="Redirect URI of the client app.",
        ),
    ],
    description: Annotated[
        str,
        typer.Option(
            "--description",
            "-d",
            help="Description of the client app.",
        ),
    ] = "",
    include_kind_0: Annotated[
        bool,
        typer.Option(
            "--include-0/--no-include-0",
            "-p/-P",
            help="Publish kind 0 event.",
        ),
    ] = False,
    include_kind_13195: Annotated[
        bool,
        typer.Option(
            "--13195/--no-13195",
            "-c/-C",
            help="Publish kind 13195 event.",
        ),
    ] = True,
):
    keys = Keys.parse(nsec)
    print("Publishing client app identity events...")
    print(f"Name: {name}")
    print(f"Image: {image}")
    print(f"NIP-05: {nip05}")
    print(f"Description: {description}")
    print(f"Redirect URIs: {redirect_uris}")
    print(f"Include kind 0: {include_kind_0}")
    print(f"Include kind 13195: {include_kind_13195}")
    typer.confirm("This will override any existing events. Are you sure?", abort=True)
    asyncio.run(
        publish_client_app_info(
            keys=keys,
            relays=relays,
            name=name,
            image=image,
            nip05=nip05,
            redirect_uris=redirect_uris,
            description=description,
            include_kind_0=include_kind_0,
            include_kind_13195=include_kind_13195,
        )
    )


async def publish_client_app_info(
    keys: Keys,
    relays: list[str],
    name: str,
    image: str,
    nip05: str,
    redirect_uris: list[str],
    description: str,
    include_kind_0: bool,
    include_kind_13195: bool,
):
    signer = NostrSigner.keys(keys)
    client = Client(signer)
    await client.add_relays(relays)
    await client.connect()

    if include_kind_0:
        print("Publishing kind 0 event...")
        await client.set_metadata(
            Metadata.from_record(
                r=MetadataRecord(
                    name=name,
                    display_name=name,
                    picture=image,
                    nip05=nip05,
                    about=description,
                )
            )
        )
    if include_kind_13195:
        builder = EventBuilder(
            kind=Kind(13195),
            content=json.dumps(
                {
                    "name": name,
                    "image": image,
                    "nip05": nip05,
                    "description": description,
                    "allowed_redirect_uris": redirect_uris,
                }
            ),
            tags=[],
        )
        print("Publishing kind 13195 event...")
        await client.send_event_builder(builder)

    await client.disconnect()
    print("Events published")


@app.command(help="Lookup client app info by npub and relay.")
def lookup(
    npub: Annotated[
        str,
        typer.Option(
            "--npub",
            "-p",
            help="Public key to lookup the client app info.",
            prompt=True,
        ),
    ],
    relay: Annotated[
        str,
        typer.Option(
            "--relay",
            "-r",
            help="Relay to lookup the client app info.",
            prompt=True,
        ),
    ],
) -> None:
    print("Looking up client app info...")
    public_key = PublicKey.parse(npub)
    asyncio.run(lookup_client_app_info(public_key, relay))


async def lookup_client_app_info(public_key: PublicKey, relay: str):
    client = Client()
    await client.add_relays([relay])
    await client.connect()
    event_filter = Filter().kinds([Kind(0), Kind(13195)]).author(public_key)
    events = await client.get_events_of([event_filter], timedelta(seconds=10))
    await client.disconnect()
    if not events:
        print("No events found")
        return

    for event in events:
        print(json.dumps(json.loads(event.content()), indent=2))


if __name__ == "__main__":
    app()
