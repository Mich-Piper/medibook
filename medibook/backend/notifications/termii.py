# backend/notifications/termii.py
import requests
from django.conf import settings


class TermiiError(Exception):
    pass


def send_sms(phone_number: str, message: str) -> dict:
    """
    Send an SMS via the Termii API.

    Args:
        phone_number: E.164 format preferred, e.g. '+2348012345678'
        message: SMS body text (max 160 chars for single SMS)

    Returns:
        Termii API response dict

    Raises:
        TermiiError: if the API call fails or returns an error status
    """
    # Normalise Nigerian numbers — strip leading 0 and add country code
    if phone_number.startswith('0'):
        phone_number = '234' + phone_number[1:]
    elif phone_number.startswith('+'):
        phone_number = phone_number[1:]

    payload = {
        'to':      phone_number,
        'from':    settings.TERMII_SENDER_ID,
        'sms':     message,
        'type':    'plain',
        'api_key': settings.TERMII_API_KEY,
        'channel': 'generic',
    }

    try:
        response = requests.post(
            'https://api.ng.termii.com/api/sms/send',
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise TermiiError(f"Termii request failed: {exc}") from exc

    if data.get('code') not in ('ok', None):
        raise TermiiError(f"Termii error: {data.get('message', 'Unknown error')}")

    return data
