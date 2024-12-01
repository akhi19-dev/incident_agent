from prisma import Prisma

# Singleton instance of the Prisma client
_prisma_client = None


async def init_prisma_client():
    """
    Initializes the Prisma client and establishes a connection to the database.
    """
    global _prisma_client
    if _prisma_client is None:
        _prisma_client = Prisma()
        await _prisma_client.disconnect()
        await _prisma_client.connect()
        print("Prisma client connected.")
    return _prisma_client


async def disconnect_prisma_client():
    """
    Disconnects the Prisma client from the database.
    """
    global _prisma_client
    if _prisma_client is not None:
        await _prisma_client.disconnect()
        print("Prisma client disconnected.")
        _prisma_client = None


def get_prisma_client():
    """
    Returns the initialized Prisma client if it's connected.

    Raises:
        Exception: If Prisma client is not initialized or connected.
    """
    if _prisma_client is None:
        raise Exception(
            "Prisma client is not connected. Please call 'init_prisma_client()' first."
        )
    return _prisma_client
