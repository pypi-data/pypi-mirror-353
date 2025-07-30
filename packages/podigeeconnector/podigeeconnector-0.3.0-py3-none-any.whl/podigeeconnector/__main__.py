"""
This is the main entry point for the Podigee Connector.
"""

import json
import os
from loguru import logger
from .connector import PodigeeConnector


def load_env_var(var_name: str) -> str:
    """
    Load environment variable or throw error
    """
    var = os.environ.get(var_name)
    if var is None or var == "":
        raise ValueError(f"Environment variable {var_name} must be set.")
    return var


def main():
    """
    Main entry point for the Podigee Connector.
    """
    base_url = load_env_var("PODIGEE_BASE_URL")
    podcast_id = load_env_var("PODCAST_ID")

    # This can be empty, in which case the session token will be used
    podigee_access_token = os.environ.get("PODIGEE_ACCESS_TOKEN")

    # This can be empty, in which case the username and password will be used
    podigee_session_v5 = os.environ.get("PODIGEE_SESSION_V5")

    if podigee_access_token:
        logger.info("Using Podigee Access Token for authentication")
        logger.debug("Token = {}...", podigee_access_token[:8])
        connector = PodigeeConnector(
            base_url=base_url,
            podigee_access_token=podigee_access_token,
        )
    elif podigee_session_v5:
        logger.info("Using Podigee Session V5 for authentication")
        # Fallback: Use session token to log in
        connector = PodigeeConnector(
            base_url,
            podigee_session_v5,
        )
    else:
        # Fallback: Use username and password to log in
        logger.info("Using Podigee Username and Password for authentication")
        username = load_env_var("PODIGEE_USERNAME")
        password = load_env_var("PODIGEE_PASSWORD")
        connector = PodigeeConnector.from_credentials(
            base_url=base_url,
            username=username,
            password=password,
        )

    podcasts = connector.podcasts()
    logger.info("Podcasts = {}", json.dumps(podcasts, indent=4))

    if not podcasts:
        logger.error("No podcasts found")
        return

    # Sort podcasts by last episode
    podcasts.sort(key=lambda x: x["last_episode_publication_date"], reverse=True)

    # Take the most recent podcast
    podcast = podcasts[0]
    podcast_id = podcast["id"]
    logger.info("Using podcast {}: {}", podcast_id, podcast["title"])

    podcast_overview = connector.podcast_overview(podcast_id)
    logger.info("Podcast Overview = {}", json.dumps(podcast_overview, indent=4))

    podcast_analytics = connector.podcast_analytics(podcast_id)
    logger.info("Podcast Analytics = {}", json.dumps(podcast_analytics, indent=4))

    episodes = connector.episodes(podcast_id)
    logger.info("Episodes = {}", json.dumps(episodes, indent=4))

    for episode in episodes:
        episode_id = episode["id"]
        episode_analytics = connector.episode_analytics(episode_id)
        logger.info(
            "Episode {} = {}", episode_id, json.dumps(episode_analytics, indent=4)
        )


if __name__ == "__main__":
    main()
