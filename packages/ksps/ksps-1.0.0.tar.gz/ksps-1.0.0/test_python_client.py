#!/usr/bin/env python3
"""
Test du client Python KPS (Ksmux Pub Sub) ultra-performant
Démontre toutes les fonctionnalités ACK identiques au client Go
"""

import asyncio
import logging
import time
from src.ksps.client import Client, ClientAck

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_python_client():
    """Test complet du client Python avec ACK"""
    print("🐍 === TEST CLIENT PYTHON ULTRA-PERFORMANT ===")
    
    try:
        # 1. Créer le client Python
        print("\n📱 Création du client Python...")
        client = await Client.NewClient(
            Id="python-test-client",
            Address="localhost:9313",
            Autorestart=True,
            OnId=lambda data, unsub: print(f"📬 Python reçu direct: {data}"),
            OnDataWs=lambda data, conn: print(f"🔔 Python message: {data.get('action', 'unknown')}")
        )
        
        print(f"✅ Client Python connecté avec ID: {client.Id}")
        
        # 2. Souscrire à des topics
        print("\n📡 Souscription aux topics...")
        
        def handle_test_topic(data, unsub):
            print(f"🔔 Python reçu sur test_topic: {data}")
        
        def handle_ack_topic(data, unsub):
            print(f"🔔 Python reçu sur ack_topic: {data}")
        
        unsub1 = await client.Subscribe("test_topic", handle_test_topic)
        unsub2 = await client.Subscribe("ack_topic", handle_ack_topic)
        
        # Attendre un peu pour la synchronisation
        await asyncio.sleep(1)
        
        # 3. Tests de publication simple
        print("\n📤 Tests de publication simple...")
        await client.Publish("test_topic", "Hello from Python!")
        await client.PublishToID("server-id", "Message direct vers serveur")
        
        await asyncio.sleep(1)
        
        # 4. Tests ACK - PublishWithAck
        print("\n🧪 === TESTS ACK PYTHON ===")
        
        print("\n1️⃣ Python.PublishWithAck(ack_topic)")
        ack1 = await client.PublishWithAck("ack_topic", "Message ACK depuis Python", 5.0)
        
        # Attendre les ACK en arrière-plan
        async def wait_ack1():
            responses = await ack1.Wait()
            print(f"📬 Python ACK reçus: {len(responses)} réponses")
            for client_id, resp in responses.items():
                if resp.get('success'):
                    print(f"✅ Python ACK de {client_id}: succès")
                else:
                    print(f"❌ Python ACK de {client_id}: erreur - {resp.get('error', 'unknown')}")
        
        asyncio.create_task(wait_ack1())
        
        await asyncio.sleep(2)
        
        # 5. Test PublishToIDWithAck
        print("\n2️⃣ Python.PublishToIDWithAck(serveur)")
        ack2 = await client.PublishToIDWithAck("server-id", "Message direct ACK Python", 3.0)
        
        async def wait_ack2():
            resp, ok = await ack2.WaitAny()
            if ok:
                print(f"📬 Python premier ACK direct reçu: {resp.get('success', False)}")
            else:
                print("⏰ Python timeout ACK direct")
        
        asyncio.create_task(wait_ack2())
        
        await asyncio.sleep(2)
        
        # 6. Test GetStatus
        print("\n3️⃣ Python Test GetStatus")
        ack3 = await client.PublishWithAck("ack_topic", "Test statut Python", 10.0)
        
        async def test_status():
            await asyncio.sleep(0.5)
            status = await ack3.GetStatus()
            print(f"📊 Python Statut ACK: {status}")
            print(f"🏁 Python Complet: {await ack3.IsComplete()}")
        
        asyncio.create_task(test_status())
        
        await asyncio.sleep(2)
        
        # 7. Test Cancel
        print("\n4️⃣ Python Test Cancel")
        ack4 = await client.PublishWithAck("ack_topic", "Test cancel Python", 10.0)
        
        async def test_cancel():
            await asyncio.sleep(1)
            print("🚫 Python Annulation de l'ACK...")
            await ack4.Cancel()
            
            # Essayer d'attendre après cancel
            responses = await ack4.Wait()
            print(f"📬 Python Réponses après cancel: {len(responses)} (devrait être 0)")
        
        asyncio.create_task(test_cancel())
        
        await asyncio.sleep(3)
        
        # 8. Test de performance
        print("\n⚡ Test de performance Python...")
        start_time = time.time()
        
        # Publier 100 messages rapidement
        tasks = []
        for i in range(100):
            task = client.Publish("test_topic", f"Message rapide {i}")
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"📊 Python: 100 messages publiés en {duration:.3f}s ({100/duration:.0f} msg/s)")
        
        # 9. Test ACK en masse
        print("\n🚀 Test ACK en masse Python...")
        start_time = time.time()
        
        ack_tasks = []
        for i in range(10):
            ack = await client.PublishWithAck("ack_topic", f"ACK masse {i}", 5.0)
            ack_tasks.append(ack.Wait())
        
        all_responses = await asyncio.gather(*ack_tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        total_acks = sum(len(responses) for responses in all_responses)
        print(f"📊 Python: {total_acks} ACK reçus en {duration:.3f}s ({total_acks/duration:.0f} ACK/s)")
        
        # 10. Garder le client en vie un moment
        print("\n⏳ Client Python en vie pendant 5 secondes...")
        await asyncio.sleep(5)
        
        print("\n✅ Tests Python terminés avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur dans les tests Python: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Nettoyer
        if 'client' in locals():
            await client.Close()
            print("🔒 Client Python fermé")

async def main():
    """Point d'entrée principal"""
    print("🐍 Démarrage des tests du client Python...")
    
    # Attendre un peu pour que le serveur soit prêt
    await asyncio.sleep(1)
    
    await test_python_client()

def setup_optimal_environment():
    """Configure l'environnement optimal pour les tests"""
    # uvloop pour performance maximale
    try:
        import uvloop
        uvloop.install()
        print("🚀 uvloop activé pour performance maximale")
    except ImportError:
        print("ℹ️ uvloop non disponible, utilisation de l'event loop standard")
    
    # orjson pour JSON ultra-rapide
    try:
        import orjson
        print("🚀 orjson disponible pour JSON ultra-rapide")
    except ImportError:
        print("ℹ️ orjson non disponible, utilisation de json standard")

if __name__ == "__main__":
    print("🐍 === KPS (KSMUX PUB SUB) PYTHON CLIENT ULTRA-PERFORMANT ===")
    print("Optimisé avec uv, uvloop, orjson et asyncio")
    
    # Setup environnement optimal
    setup_optimal_environment()
    
    # Lancer les tests
    asyncio.run(main()) 