"""
KPS - Ksmux Pub Sub: Client Python ultra-performant

Un client Python asyncio ultra-rapide pour système pub/sub basé sur ksmux,
avec support complet des ACK, optimisé avec uvloop et orjson pour des performances maximales.

Exemple d'usage:
    import asyncio
    from ksps import Client

    async def main():
        client = await Client.NewClient(
            Id="my-app",
            Address="localhost:9313"
        )
        
        # Souscrire à un topic
        await client.Subscribe("events", 
            lambda data, unsub: print(f"Reçu: {data}"))
        
        # Publier avec ACK
        ack = await client.PublishWithAck("events", "Hello!", 5.0)
        responses = await ack.Wait()
        
        await client.Close()

    asyncio.run(main())
"""

from .client import Client, ClientAck, ClientSubscriber, ClientSubscription

__version__ = "1.0.0"
__author__ = "Kamal Shkeir"
__email__ = "kamalshkeir@gmail.com"
__description__ = "KPS - Ksmux Pub Sub: Client Python ultra-performant"

__all__ = [
    "Client",
    "ClientAck", 
    "ClientSubscriber",
    "ClientSubscription",
]

# Alias pour compatibilité
BusClient = Client 