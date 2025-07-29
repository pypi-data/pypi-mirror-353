#!/usr/bin/env python3
"""
Test simple du client KPS (Ksmux Pub Sub) pour vérifier l'installation
"""

import asyncio
import sys
from .client import Client

async def test_connection():
    """Test de connexion basique"""
    print("🧪 Test de connexion au serveur KPS...")
    
    try:
        client = await Client.NewClient(
            Id="test-install-client",
            Address="localhost:9313",
            OnId=lambda data, unsub: print(f"📬 Reçu: {data}")
        )
        
        print("✅ Connexion réussie!")
        
        # Test basique
        await client.Subscribe("test", lambda data, unsub: print(f"📨 Test: {data}"))
        await client.Publish("test", "Hello from KPS!")
        
        await asyncio.sleep(1)
        await client.Close()
        
        print("✅ Test terminé avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print("💡 Assurez-vous que le serveur BBUS tourne sur localhost:9313")
        return False

def main():
    """Point d'entrée pour le script bbus-test"""
    print("🐍 BBUS Python Client - Test d'Installation")
    print("=" * 50)
    
    try:
        success = asyncio.run(test_connection())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrompu")
        sys.exit(1)

if __name__ == "__main__":
    main() 