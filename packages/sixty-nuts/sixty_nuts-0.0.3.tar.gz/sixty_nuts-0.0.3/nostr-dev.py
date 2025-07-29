#!/usr/bin/env python3
"""Simple script to fetch all events from a given nsec."""

import asyncio
import sys
from datetime import datetime
from typing import Any

# For secp256k1 key operations
try:
    from coincurve import PrivateKey
except ImportError:
    print("Please install coincurve: pip install coincurve")
    sys.exit(1)

from sixty_nuts.relay import NostrRelay, NostrFilter


# Common Nostr relays
DEFAULT_RELAYS = [
    "wss://relay.damus.io",
    "wss://nos.lol",
    "wss://relay.nostr.band",
    "wss://relay.snort.social",
]

# Common event kinds for reference
EVENT_KINDS = {
    0: "Profile metadata",
    1: "Text note",
    2: "Recommend relay",
    3: "Contact list",
    4: "Encrypted direct message",
    5: "Event deletion",
    6: "Repost",
    7: "Reaction",
    40: "Channel creation",
    41: "Channel metadata",
    42: "Channel message",
    43: "Channel hide message",
    44: "Channel mute user",
    1984: "Reporting",
    9734: "Zap request",
    9735: "Zap",
    10000: "Mute list",
    10001: "Pin list",
    10002: "Relay list metadata",
    10019: "Relay recommendations",
    17375: "NIP-60 wallet metadata",
    7374: "NIP-60 quote",
    7375: "NIP-60 token",
    7376: "NIP-60 history",
}


def bech32_decode(bech: str) -> tuple[str, bytes]:
    """Decode bech32 string and return hrp and data."""
    CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

    if not bech:
        raise ValueError("Empty bech32 string")

    bech = bech.lower()
    pos = bech.rfind("1")
    if pos < 1 or pos + 7 > len(bech) or pos + 1 + 6 > len(bech):
        raise ValueError("Invalid bech32 format")

    hrp = bech[:pos]
    data = bech[pos + 1 :]

    # Convert data part to integers
    decoded = []
    for char in data:
        if char not in CHARSET:
            raise ValueError(f"Invalid character in bech32: {char}")
        decoded.append(CHARSET.index(char))

    # Verify checksum (simplified - not implementing full bech32 verification)
    if len(decoded) < 6:
        raise ValueError("Invalid bech32 data length")

    # Convert from 5-bit to 8-bit
    data_part = decoded[:-6]  # Remove checksum

    # Convert 5-bit groups to bytes
    bits = 0
    value = 0
    result = []

    for group in data_part:
        value = (value << 5) | group
        bits += 5
        if bits >= 8:
            result.append((value >> (bits - 8)) & 255)
            bits -= 8

    if bits >= 5:
        raise ValueError("Invalid padding in bech32")

    return hrp, bytes(result)


def nsec_to_pubkey(nsec: str) -> str:
    """Convert nsec to hex pubkey."""
    try:
        hrp, data = bech32_decode(nsec)

        if hrp != "nsec":
            raise ValueError("Not a valid nsec (expected 'nsec' prefix)")

        if len(data) != 32:
            raise ValueError("Invalid private key length")

        # Create coincurve private key and derive public key
        private_key = PrivateKey(data)
        public_key_bytes = private_key.public_key.format(compressed=True)

        # Return hex pubkey (skip the first byte which is the compression flag)
        return public_key_bytes[1:].hex()

    except Exception as e:
        raise ValueError(f"Invalid nsec: {e}")


def format_timestamp(timestamp: int) -> str:
    """Format Unix timestamp to readable string."""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def get_kind_description(kind: int) -> str:
    """Get human-readable description for event kind."""
    return EVENT_KINDS.get(kind, f"Unknown kind {kind}")


async def fetch_events_from_relay(
    relay_url: str, pubkey: str, kinds: list[int] | None = None, limit: int = 50
) -> list[Any]:
    """Fetch events from a single relay."""
    relay = NostrRelay(relay_url)

    try:
        print(f"Connecting to {relay_url}...")

        # Build filter
        filter_dict: NostrFilter = {
            "authors": [pubkey],
            "limit": limit,
        }

        # Add kinds filter if specified
        if kinds is not None:
            filter_dict["kinds"] = kinds

        filters: list[NostrFilter] = [filter_dict]

        events = await relay.fetch_events(filters, timeout=10.0)
        print(f"  Found {len(events)} events from {relay_url}")
        return events

    except Exception as e:
        print(f"  Error fetching from {relay_url}: {e}")
        return []
    finally:
        await relay.disconnect()


async def fetch_all_events(
    nsec: str,
    relays: list[str] | None = None,
    kinds: list[int] | None = None,
    limit: int = 50,
) -> None:
    """Fetch all events from the given nsec across multiple relays."""

    # Convert nsec to pubkey
    try:
        pubkey = nsec_to_pubkey(nsec)
        print(f"Fetching events for pubkey: {pubkey}")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Use default relays if none provided
    if relays is None:
        relays = DEFAULT_RELAYS

    kinds_str = f" (kinds: {kinds})" if kinds else " (all kinds)"
    print(f"Searching {len(relays)} relays{kinds_str}...")

    # Fetch from all relays in parallel
    tasks = [fetch_events_from_relay(relay, pubkey, kinds, limit) for relay in relays]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect all events and deduplicate by ID
    all_events = {}
    for result in results:
        if isinstance(result, list):
            for event in result:
                all_events[event["id"]] = event

    # Sort by creation time (newest first)
    events = sorted(all_events.values(), key=lambda x: x["created_at"], reverse=True)

    print(f"\n=== Found {len(events)} unique events ===\n")

    # Display the events
    for i, event in enumerate(events, 1):
        kind_desc = get_kind_description(event["kind"])
        print(f"[{i}] {format_timestamp(event['created_at'])}")
        print(f"Kind: {event['kind']} ({kind_desc})")
        print(f"ID: {event['id']}")
        print(
            f"Content: {event['content'][:200]}{'...' if len(event['content']) > 200 else ''}"
        )

        # Show tags if any
        if event["tags"]:
            print(f"Tags: {len(event['tags'])} tag(s)")
            for tag in event["tags"][:3]:  # Show first 3 tags
                print(f"  {tag}")
            if len(event["tags"]) > 3:
                print(f"  ... and {len(event['tags']) - 3} more")

        print("-" * 80)


def parse_kinds(kinds_str: str) -> list[int]:
    """Parse comma-separated kinds string into list of integers."""
    try:
        return [int(k.strip()) for k in kinds_str.split(",") if k.strip()]
    except ValueError as e:
        raise ValueError(f"Invalid kind number: {e}")


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python nostr-dev.py <nsec> [--kinds=1,17375] [relay_urls...]")
        print("\nExamples:")
        print("  python nostr-dev.py nsec1...                    # Fetch all kinds")
        print("  python nostr-dev.py nsec1... --kinds=1          # Only notes")
        print(
            "  python nostr-dev.py nsec1... --kinds=1,17375    # Notes and wallet metadata"
        )
        print("  python nostr-dev.py nsec1... wss://relay.damus.io  # Custom relay")
        print("\nCommon event kinds:")
        for kind, desc in sorted(EVENT_KINDS.items()):
            print(f"  {kind}: {desc}")
        return

    nsec = sys.argv[1]

    # Parse arguments
    kinds = None
    custom_relays = []

    for arg in sys.argv[2:]:
        if arg.startswith("--kinds="):
            kinds_str = arg[8:]  # Remove "--kinds="
            try:
                kinds = parse_kinds(kinds_str)
                print(f"Filtering for kinds: {kinds}")
            except ValueError as e:
                print(f"Error parsing kinds: {e}")
                return
        elif arg.startswith("wss://") or arg.startswith("ws://"):
            custom_relays.append(arg)
        else:
            print(f"Unknown argument: {arg}")
            return

    relay_list = custom_relays if custom_relays else None
    await fetch_all_events(nsec, relay_list, kinds)


if __name__ == "__main__":
    asyncio.run(main())
