# UMA Auth CLI

A simple CLI tool for working with UMA auth. Can help with generating new nostr keys and publishing client app info events.

## Installation

To run the CLI from source, you can clone this repository and run:

```bash
pipenv install --dev
pipenv run python -m build
pip install dist/*.whl
```

You can then run the CLI from anywhere:

```bash
uma-auth-cli --help
```

To install the CLI as a package from pypi instead, you can run:

```bash
# Note: This is not yet published to pypi.
pip install uma-auth-cli
```

## Usage

### Key Generation

To generate a new nostr keypair, run:

```bash
uma-auth-cli generate-key
```

It will create and print a new keypair in hex and bech32 format:

```bash
nsec1e792rulwmsjanw783x39r8vcm23c2hwcandwahaw6wh39rfydshqxhfm7x
npub13msd7fakpaqerq036kk0c6pf9effz5nn5yk6nqj4gtwtzr5l6fxq64z8x5

sec hex: cf8aa1f3eedc25d9bbc789a2519d98daa3855dd8ecdaeedfaed3af128d246c2e
pub hex: 8ee0df27b60f419181f1d5acfc68292e52915273a12da9825542dcb10e9fd24c
```

### Publishing client app info

You can publish a client app info (kind 13195 and optionally kind 0) using the CLI. The CLI can publish these events in interactive prompt mode:

```bash
$ uma-auth-cli publish \
--nsec nsec1mqxnulkqkcv0gc0dfrxz5kz7d3h665ve2dhjkrj8jmmxwm4st2zsjv2n5l \
--relay wss://nos.lol --relay wss://relay.primal.net \
--redirect-uri https://foo.test \
--image https://foo.com/image.png \
--nip05 _@foo.com \
--include-0 \
--name "Test CLI" \
--description "A test client app"
```

### Looking up client app info

You can look up client app info using the CLI:

```bash
$ uma-auth-cli lookup \
--npub npub13msd7fakpaqerq036kk0c6pf9effz5nn5yk6nqj4gtwtzr5l6fxq64z8x5 \
--relay wss://nos.lol
```

### Authority Verification

As per [NIP-68](https://github.com/nostr-protocol/nips/pull/1383/), you can act as the authority or check authority attestations using the CLI.

#### Attesting to an app's identity

First, find the app 13195 event ID by using the lookup command. Then, you can attest to the app's identity:

```bash
$ uma-auth-cli attest \
--nsec nsec1mqxnulkqkcv0gc0dfrxz5kz7d3h665ve2dhjkrj8jmmxwm4st2zsjv2n5l \
--relay wss://nos.lol \
--app-npub npub13msd7fakpaqerq036kk0c6pf9effz5nn5yk6nqj4gtwtzr5l6fxq64z8x5 \
--event-id bb892e7d7a26e88fe668e65c75eed7fd11619bf6512e8fe12d5bf3ba5db10c90
```

- `--nsec` is the nostr keypair secret key of the authority attesting to the app's identity.
- `--relay` is the relay to use to publish the attestation.
- `--app-npub` is the clients app's public key.
- `--event-id` is the event ID of the app's 13195 event.

#### Looking up attestations

You can look up attestations using the CLI:

```bash
$ uma-auth-cli lookup \
--authority nprofile1qqstse98yvaykl3k2yez3732tmsc9vaq8c3uhex0s4qp4dl8fczmp9spp4mhxue69uhkummn9ekx7mq26saje \
--npub npub13msd7fakpaqerq036kk0c6pf9effz5nn5yk6nqj4gtwtzr5l6fxq64z8x5 \
--relay wss://nos.lol
```
