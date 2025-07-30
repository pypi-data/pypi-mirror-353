# Copyright 2024 CS Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""osam main module."""

import asyncio  # for handling asynchronous tasks
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException
from osam.tasks import (
    build_s3_rights,
    build_users_data_map,
    link_rspython_users_and_obs_users,
)
from rs_server_common.utils import init_opentelemetry
from rs_server_common.utils.logging import Logging
from starlette.requests import Request  # pylint: disable=C0411
from starlette.responses import JSONResponse
from starlette.status import (  # pylint: disable=C0411
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

DEFAULT_OSAM_FREQUENCY_SYNC = int(os.environ.get("DEFAULT_OSAM_FREQUENCY_SYNC", 3600))

# Initialize a FastAPI application
app = FastAPI(title="osam-service", root_path="", debug=True)
router = APIRouter(tags=["OSAM service"])

logger = Logging.default(__name__)
logger.setLevel(logging.DEBUG)


@asynccontextmanager
async def app_lifespan(fastapi_app: FastAPI):
    """Lifespann app to be implemented with start up / stop logic"""
    logger.info("Starting up the application...")
    fastapi_app.extra["shutdown_event"] = asyncio.Event()
    # the following event may be called from the future endpoint requested in rspy 606
    fastapi_app.extra["endpoint_trigger"] = asyncio.Event()
    # Run the refresh loop in the background
    fastapi_app.extra["refresh_task"] = asyncio.get_event_loop().create_task(
        main_osam_task(timeout=DEFAULT_OSAM_FREQUENCY_SYNC),
    )
    fastapi_app.extra["users_info"] = dict[str, Any]
    # Yield control back to the application (this is where the app will run)
    yield

    # Shutdown logic (cleanup)
    logger.info("Shutting down the application...")
    # Cancel the refresh task and wait for it to exit cleanly
    fastapi_app.extra["shutdown_event"].set()
    refresh_task = fastapi_app.extra.get("refresh_task")
    if refresh_task:
        refresh_task.cancel()
        try:
            await refresh_task  # Ensure the task exits
        except asyncio.CancelledError:
            pass  # Ignore the cancellation exception
    logger.info("Application gracefully stopped...")


@router.post("/storage/accounts/update")
async def accounts_update():
    """Used as a trigger to link the keycloak users to the obs users
    It also creates the s3 access rights for each user
    """
    logger.debug("Endpoint for triggering the users synchronization process called")
    # app.extra["endpoint_trigger"].set()
    try:
        link_rspython_users_and_obs_users()
        app.extra["users_info"] = build_users_data_map()
        return JSONResponse(status_code=HTTP_200_OK, content="Keycloak and OVH accounts updated")
    except RuntimeError as rt:
        return HTTPException(
            HTTP_500_INTERNAL_SERVER_ERROR,
            f"Failed to update the keycloack and ovh accounts. Reason: {rt}",
        )


@router.get("/storage/account/{user}/rights")
async def user_rights(request: Request, user: str):  # pylint: disable=unused-argument
    """Used as a trigger to link the keycloak users to the obs users
    It also creates the s3 access rights for each user
    """
    logger.debug("Endpoint for getting the user rights")
    if user not in app.extra["users_info"]:
        return HTTPException(HTTP_404_NOT_FOUND, f"User '{user}' does not exist in keycloak")
    logger.debug(f"Building the rights for user {app.extra['users_info'][user]}")
    output = build_s3_rights(app.extra["users_info"][user])
    return JSONResponse(status_code=HTTP_200_OK, content=output)


async def main_osam_task(timeout: int = 60):
    """
    Asynchronous background task that periodically links RS-Python users to observation users.

    This function continuously waits for either a shutdown signal or an external trigger (`endpoint_trigger`)
    to perform synchronization of Keycloak user attributes using `link_rspython_users_and_obs_users()`.
    The loop exits gracefully on shutdown signal.

    Args:
        timeout (int, optional): Number of seconds to wait before checking for shutdown or trigger events.
                                 Defaults to 60 seconds.

    Returns:
        None

    Raises:
        RuntimeError: This function does not explicitly raise `RuntimeError`, but any internal failure
                      is logged, and the task continues unless a shutdown signal is received.
    """
    logger.info("Starting the main background thread ")
    original_timeout = timeout
    while True:
        try:
            # Wait for either the shutdown event or the timeout before starting the refresh process
            # for getting attributes from keycloack

            await asyncio.wait(
                {
                    asyncio.create_task(app.extra["shutdown_event"].wait()),
                    asyncio.create_task(app.extra["endpoint_trigger"].wait()),
                },
                timeout=original_timeout,  # Wait up to timeout seconds before waking up
                return_when=asyncio.FIRST_COMPLETED,
            )

            if app.extra["shutdown_event"].is_set():  # If shutting down, exit loop
                logger.info("Finishing the main background thread  and exit")
                break
            if app.extra["endpoint_trigger"].is_set():  # If triggered, prepare for the next one
                logger.debug("Releasing endpoint_trigger")
                app.extra["endpoint_trigger"].clear()

            logger.debug("Starting the process to get the keycloack attributes ")

            link_rspython_users_and_obs_users()
            app.extra["users_info"] = build_users_data_map()

            logger.debug("Getting the keycloack attributes finished")

        except Exception as e:  # pylint: disable=broad-exception-caught
            # Handle cancellation properly even for asyncio.CancelledError (for example when FastAPI shuts down)
            logger.exception(f"Handle cancellation: {e}")
            # let's continue
    logger.info("Exiting from the getting keycloack attributes thread !")
    return


# Health check route
@router.get("/_mgmt/ping", include_in_schema=False)
async def ping():
    """Liveliness probe."""
    return JSONResponse(status_code=HTTP_200_OK, content="Healthy")


app.include_router(router)
app.router.lifespan_context = app_lifespan  # type: ignore
init_opentelemetry.init_traces(app, "osam.service")
