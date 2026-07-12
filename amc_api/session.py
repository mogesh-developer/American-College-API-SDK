import requests

from .config import Config
from .logger import logger


class AMCSession:

    def __init__(self, config: Config):

        self.config = config

        self.session = requests.Session()

        self.api_token = None

        self.reauth_callback = None
        self.token_update_callback = None

        self.session.headers.update({
            "User-Agent": config.user_agent,
            "Accept": "application/json",
            "Origin": config.base_url,
            "Referer": f"{config.base_url}/mob/",
            "X-Requested-With": "XMLHttpRequest"
        })

    def set_token(self, token):

        self.api_token = token

        self.session.headers.update({
            "api-token": token
        })

        if self.token_update_callback:
            try:
                self.token_update_callback(token)
            except Exception:
                pass

    def _is_token_expired(self, response):

        if response.status_code == 401:
            return True

        try:
            data = response.json()
            # If the response explicitly states token error
            msg = str(data.get("message", "")).lower()
            status = str(data.get("status", "")).lower()
            errorcode = str(data.get("errorcode", ""))

            if errorcode == "401" or "invalid token" in msg or "token expired" in msg or status == "invalid_token":
                return True
        except Exception:
            pass

        return False

    def post(self, url, **kwargs):

        kwargs.setdefault(
            "timeout",
            self.config.timeout
        )

        kwargs.setdefault(
            "verify",
            self.config.verify_ssl
        )

        logger.info("POST %s", url)

        response = self.session.post(
            url,
            **kwargs
        )

        logger.info(
            "POST %s %d %s",
            url,
            response.status_code,
            response.reason
        )

        # Token retry logic
        if self._is_token_expired(response) and self.reauth_callback:
            logger.info("Token expired/invalid. Attempting automatic re-authentication...")
            try:
                self.reauth_callback()
                # Update headers for retry
                if self.api_token:
                    if "headers" not in kwargs:
                        kwargs["headers"] = {}
                    kwargs["headers"]["api-token"] = self.api_token

                logger.info("Retrying POST %s after re-authentication", url)
                response = self.session.post(url, **kwargs)
                logger.info(
                    "Retry POST %s %d %s",
                    url,
                    response.status_code,
                    response.reason
                )
            except Exception as e:
                logger.error("Failed to automatically re-authenticate: %s", str(e))

        return response

    def get(self, url, **kwargs):

        kwargs.setdefault(
            "timeout",
            self.config.timeout
        )

        kwargs.setdefault(
            "verify",
            self.config.verify_ssl
        )

        logger.info("GET %s", url)

        response = self.session.get(
            url,
            **kwargs
        )

        logger.info(
            "GET %s %d %s",
            url,
            response.status_code,
            response.reason
        )

        # Token retry logic
        if self._is_token_expired(response) and self.reauth_callback:
            logger.info("Token expired/invalid. Attempting automatic re-authentication...")
            try:
                self.reauth_callback()
                # Update headers for retry
                if self.api_token:
                    if "headers" not in kwargs:
                        kwargs["headers"] = {}
                    kwargs["headers"]["api-token"] = self.api_token

                logger.info("Retrying GET %s after re-authentication", url)
                response = self.session.get(url, **kwargs)
                logger.info(
                    "Retry GET %s %d %s",
                    url,
                    response.status_code,
                    response.reason
                )
            except Exception as e:
                logger.error("Failed to automatically re-authenticate: %s", str(e))

        return response
