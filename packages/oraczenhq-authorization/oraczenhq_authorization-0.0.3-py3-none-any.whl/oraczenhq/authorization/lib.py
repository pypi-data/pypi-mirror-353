import logging
import openfga_sdk
from typing import Optional, Any
from redis import Redis
from pydantic import BaseModel, Field
from openfga_sdk.client import OpenFgaClient
from openfga_sdk.client.models.check_request import ClientCheckRequest
from openfga_sdk.client.models.list_objects_request import ClientListObjectsRequest
from openfga_sdk.client.models.list_users_request import ClientListUsersRequest
from openfga_sdk.client.models.list_users_request import FgaObject
from openfga_sdk.client.models.list_users_request import UserTypeFilter
from openfga_sdk.client.models.tuple import ClientTuple
from openfga_sdk.client.models.write_request import ClientWriteRequest
from openfga_sdk.models.create_store_request import CreateStoreRequest

logger = logging.getLogger(__name__)

class OpenFgaConfig(BaseModel):
    store_name: str = Field(..., description="Name of the store")
    
    model_version: str = Field(..., description="Version of the store")
    model_obj: dict[str, Any] = Field(..., description="Authorization Model of the store")
    
    api_url: str = Field(..., description="The URL of the OpenFGA API")
    
    redis_host: Optional[str] = Field("http://localhost", description="The HOST of redis server")
    redis_password: Optional[str] = Field(None, description="The Password of redis server")
    redis_port: Optional[str] = Field("6379", description="The PORT of redis server")

class OpenFgaService:
    def __init__(self, config: OpenFgaConfig) -> None:
        self.store_id: str | None = None
        self.authorization_model_id: str | None = None
        self.config = config
        self._redis_client = Redis(host=config.redis_host, port=config.redis_port, password=config.redis_password)

        logger.debug("OpenFGA service instance initialized")

    def get_config(self):
        """Get OpenFGA client configuration with current store and model IDs."""
        config = openfga_sdk.ClientConfiguration(
            api_url=self.config.api_url,
            store_id=self.store_id,
            authorization_model_id=self.authorization_model_id,
        )
        logger.debug(
            "OpenFGA client configuration created",
            extra={
                "api_url": self.config.api_url,
                "store_id": self.store_id,
                "auth_model_id": self.authorization_model_id,
            },
        )
        return config

    async def list_objects(self, from_id: str, relation: str, object_type: str):
        """List objects accessible by a user for a given relation."""
        logger.info(
            "Retrieving accessible objects for user",
            extra={"user_id": from_id, "relation": relation, "object_type": object_type},
        )

        try:
            async with OpenFgaClient(self.get_config()) as fga_client:
                request = ClientListObjectsRequest(
                    user=from_id, relation=relation, type=object_type
                )
                response = await fga_client.list_objects(request)

                objects = [object.split(":")[1] for object in response.objects]
                logger.info(
                    "Successfully retrieved accessible objects",
                    extra={
                        "user_id": from_id,
                        "relation": relation,
                        "object_type": object_type,
                        "object_count": len(objects),
                    },
                )
                return objects

        except Exception as e:
            logger.error(
                "Failed to retrieve accessible objects",
                extra={
                    "user_id": from_id,
                    "relation": relation,
                    "object_type": object_type,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def list_users(self, relation: str, object_type: str, object_id: str):
        """List users who have a specific relation to an object."""
        logger.info(
            "Retrieving users with relation to object",
            extra={"relation": relation, "object_type": object_type, "object_id": object_id},
        )

        try:
            async with OpenFgaClient(self.get_config()) as fga_client:
                userFilters = [UserTypeFilter(type="user")]
                request = ClientListUsersRequest(
                    object=FgaObject(type=object_type, id=object_id),
                    relation=relation,
                    user_filters=userFilters,
                )

                response = await fga_client.list_users(request)
                users = [user.object.id for user in response.users]

                logger.info(
                    "Successfully retrieved users with object relation",
                    extra={
                        "relation": relation,
                        "object_type": object_type,
                        "object_id": object_id,
                        "user_count": len(users),
                    },
                )
                return users

        except Exception as e:
            logger.error(
                "Failed to retrieve users with object relation",
                extra={
                    "relation": relation,
                    "object_type": object_type,
                    "object_id": object_id,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def delete_tuple(self, from_id: str, to_id: str, relation: str):
        """Delete a relationship tuple between user and object."""
        logger.info(
            "Deleting authorization tuple",
            extra={"user_id": from_id, "object_id": to_id, "relation": relation},
        )

        try:
            async with OpenFgaClient(self.get_config()) as fga_client:
                request = ClientWriteRequest(
                    deletes=[ClientTuple(user=from_id, relation=relation, object=to_id)]
                )

                response = await fga_client.write(request)

                logger.info(
                    "Authorization tuple deleted successfully",
                    extra={"user_id": from_id, "object_id": to_id, "relation": relation},
                )
                return response

        except Exception as e:
            logger.error(
                "Failed to delete authorization tuple",
                extra={
                    "user_id": from_id,
                    "object_id": to_id,
                    "relation": relation,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def check_tuple(self, from_id: str, to_id: str, relation: str):
        """Check if a relationship tuple exists between user and object."""
        logger.debug(
            "Checking authorization tuple existence",
            extra={"user_id": from_id, "object_id": to_id, "relation": relation},
        )

        try:
            async with OpenFgaClient(self.get_config()) as fga_client:
                request = ClientCheckRequest(
                    user=from_id,
                    relation=relation,
                    object=to_id,
                )

                response = await fga_client.check(request)

                logger.debug(
                    "Authorization tuple check completed",
                    extra={
                        "user_id": from_id,
                        "object_id": to_id,
                        "relation": relation,
                        "allowed": response.allowed,
                    },
                )
                return response

        except Exception as e:
            logger.error(
                "Failed to check authorization tuple",
                extra={
                    "user_id": from_id,
                    "object_id": to_id,
                    "relation": relation,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def create_tuple(self, from_id: str, to_id: str, relation: str):
        """Create a new relationship tuple between user and object."""
        logger.info(
            "Creating authorization tuple",
            extra={"user_id": from_id, "object_id": to_id, "relation": relation},
        )

        try:
            async with OpenFgaClient(self.get_config()) as fga_client:
                request = ClientWriteRequest(
                    writes=[ClientTuple(user=from_id, relation=relation, object=to_id)]
                )

                response = await fga_client.write(request)

                logger.info(
                    "Authorization tuple created successfully",
                    extra={"user_id": from_id, "object_id": to_id, "relation": relation},
                )
                return response

        except Exception as e:
            logger.error(
                "Failed to create authorization tuple",
                extra={
                    "user_id": from_id,
                    "object_id": to_id,
                    "relation": relation,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise

    async def read_auth_model(self):
        """Retrieve the latest authorization model from OpenFGA."""
        logger.info("Retrieving latest authorization model")

        try:
            async with OpenFgaClient(self.get_config()) as fga_client:
                response = await fga_client.read_latest_authorization_model()

                logger.info(
                    "Successfully retrieved authorization model",
                    extra={"model_id": response.authorization_model.id},
                )
                return response.authorization_model

        except Exception as e:
            logger.error(
                "Failed to retrieve authorization model", extra={"error": str(e)}, exc_info=True
            )
            raise

    async def setup_auth_model(self):
        """Initialize or retrieve existing authorization model."""
        logger.info(
            "Initializing authorization model", extra={"model_version": self.config.model_version}
        )

        # Check for existing authorization model in cache
        cache_key = f"openfga:{self.store_id}:auth-models:v{self.config.model_version}"

        try:
            existing_auth_model_id = self._redis_client.get(cache_key)

            if existing_auth_model_id:
                self.authorization_model_id = existing_auth_model_id.decode("utf-8")
                logger.info(
                    "Using cached authorization model",
                    extra={
                        "model_id": self.authorization_model_id,
                        "model_version": self.config.model_version,
                    },
                )
                return

            # Create new authorization model
            async with OpenFgaClient(self.get_config()) as fga_client:
                logger.info("Creating new authorization model")

                response = await fga_client.write_authorization_model(self.config.model_obj)
                self.authorization_model_id = response.authorization_model_id

                # Cache the model ID
                self._redis_client.set(cache_key, self.authorization_model_id, nx=True)

                logger.info(
                    "Authorization model created and cached successfully",
                    extra={
                        "model_id": self.authorization_model_id,
                        "model_version": self.config.model_version,
                    },
                )

        except Exception as e:
            logger.error(
                "Failed to initialize authorization model",
                extra={"model_version": self.config.model_version, "error": str(e)},
                exc_info=True,
            )
            raise

    async def setup_store(self):
        """Initialize or retrieve existing OpenFGA store."""
        logger.info("Initializing OpenFGA store", extra={"store_name": self.config.store_name})

        try:
            async with OpenFgaClient(self.get_config()) as fga_client:
                # Search for existing store
                logger.debug("Searching for existing OpenFGA store")
                store_response = await fga_client.list_stores(
                    options={"name": self.config.store_name, "page_size": 50}
                )

                stores = store_response.stores or []

                # Check if store already exists
                for store in stores:
                    if store.name == self.config.store_name:
                        self.store_id = store.id
                        logger.info(
                            "Using existing OpenFGA store",
                            extra={"store_name": self.config.store_name, "store_id": store.id},
                        )
                        return

                # Create new store if not found
                logger.info("Creating new OpenFGA store")
                response = await fga_client.create_store(
                    CreateStoreRequest(name=self.config.store_name)
                )

                self.store_id = response.id
                logger.info(
                    "OpenFGA store created successfully",
                    extra={"store_name": self.config.store_name, "store_id": self.store_id},
                )

        except Exception as e:
            logger.error(
                "Failed to initialize OpenFGA store",
                extra={"store_name": self.config.store_name, "error": str(e)},
                exc_info=True,
            )
            raise


class OpenFgaServiceSingleton:
    """Singleton pattern for OpenFGA service to ensure single instance."""

    _instance: OpenFgaService | None = None
    config: OpenFgaConfig | None = None

    @staticmethod
    def get_service() -> OpenFgaService:
        """Get or create the singleton OpenFGA service instance."""

        if not OpenFgaServiceSingleton.config:
            raise Exception("OpenFgaConfig must be set before getting the service instance.")

        if not OpenFgaServiceSingleton._instance:
            logger.debug("Creating new OpenFGA service singleton instance")
            OpenFgaServiceSingleton._instance = OpenFgaService(config=OpenFgaServiceSingleton.config)
        else:
            logger.debug("Returning existing OpenFGA service singleton instance")

        return OpenFgaServiceSingleton._instance
