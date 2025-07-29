package main

import (
	"fmt"
	"time"

	"github.com/kamalshkeir/thebus/bus"
)

func main() {
	fmt.Println("🚀 Test ACK entre serveur et client Go")

	// 1. Démarrer le serveur
	go runServer()
	time.Sleep(200 * time.Millisecond)

	// 2. Démarrer le client
	go runClient()
	time.Sleep(300 * time.Millisecond)

	// 3. Tests ACK
	runAckTests()

	fmt.Println("\nAppuyez sur Entrée pour quitter...")
	fmt.Scanln()
}

var testServer *bus.ServerBus
var testClient *bus.Client

func runServer() {
	fmt.Println("🌐 Serveur démarré")

	server := bus.NewServer()
	testServer = server

	// Subscribe local sur le serveur
	server.Subscribe("test_topic", func(data any, unsub func()) {
		fmt.Printf("🔔 Serveur reçu: %v\n", data)
	})

	// OnID pour messages directs
	server.OnID(func(data any) {
		fmt.Printf("📬 Serveur reçu message direct: %v\n", data)
	})

	server.Run()
}

func runClient() {
	fmt.Println("📱 Client démarré")

	client, err := bus.NewClient(bus.ClientConnectOptions{
		Id:      "test-client-ack",
		Address: "localhost:9313",
		OnId: func(data map[string]any, unsub bus.ClientSubscriber) {
			fmt.Printf("📬 Client reçu: %v\n", data)
		},
	})

	if err != nil {
		fmt.Printf("❌ Erreur client: %v\n", err)
		return
	}

	testClient = client

	// Subscribe du client
	client.Subscribe("test_topic", func(data any, unsub func()) {
		fmt.Printf("🔔 Client reçu topic: %v\n", data)
	})

	client.Subscribe("ack_topic", func(data any, unsub func()) {
		fmt.Printf("🔔 Client reçu ACK topic: %v\n", data)
	})
}

func runAckTests() {
	if testClient == nil || testServer == nil {
		fmt.Println("❌ Client ou serveur non initialisé")
		return
	}

	fmt.Println("\n🧪 === TESTS ACK CLIENT ===")

	// Test 1: Client.PublishWithAck
	fmt.Println("\n1️⃣ Client.PublishWithAck(ack_topic)")
	ack1 := testClient.PublishWithAck("ack_topic", "Message ACK depuis client", 5*time.Second)

	go func() {
		fmt.Println("⏳ Attente des ACK...")
		responses := ack1.Wait()
		fmt.Printf("📬 ACK reçus: %d réponses\n", len(responses))
		for clientID, resp := range responses {
			if resp.Success {
				fmt.Printf("✅ ACK de %s: succès\n", clientID)
			} else {
				fmt.Printf("❌ ACK de %s: erreur - %s\n", clientID, resp.Error)
			}
		}
	}()

	time.Sleep(2 * time.Second)

	// Test 2: Client.PublishToIDWithAck
	fmt.Println("\n2️⃣ Client.PublishToIDWithAck(serveur)")
	ack2 := testClient.PublishToIDWithAck("server-id", "Message direct ACK", 3*time.Second)

	go func() {
		resp, ok := ack2.WaitAny()
		if ok {
			fmt.Printf("📬 Premier ACK direct reçu: %v\n", resp.Success)
		} else {
			fmt.Println("⏰ Timeout ACK direct")
		}
	}()

	time.Sleep(2 * time.Second)

	// Test 3: Serveur.PublishWithAck
	fmt.Println("\n3️⃣ Serveur.PublishWithAck(ack_topic)")
	ack3 := testServer.PublishWithAck("ack_topic", "Message ACK depuis serveur", 4*time.Second)

	go func() {
		responses := ack3.Wait()
		fmt.Printf("📬 Serveur ACK reçus: %d réponses\n", len(responses))
		for clientID, resp := range responses {
			if resp.Success {
				fmt.Printf("✅ Serveur ACK de %s: succès\n", clientID)
			} else {
				fmt.Printf("❌ Serveur ACK de %s: erreur - %s\n", clientID, resp.Error)
			}
		}
	}()

	time.Sleep(2 * time.Second)

	// Test 4: GetStatus
	fmt.Println("\n4️⃣ Test GetStatus")
	ack4 := testClient.PublishWithAck("ack_topic", "Test statut", 10*time.Second)

	go func() {
		time.Sleep(500 * time.Millisecond)
		status := ack4.GetStatus()
		fmt.Printf("📊 Statut ACK: %v\n", status)
		fmt.Printf("🏁 Complet: %v\n", ack4.IsComplete())
	}()

	time.Sleep(2 * time.Second)

	// Test 5: Cancel
	fmt.Println("\n5️⃣ Test Cancel")
	ack5 := testClient.PublishWithAck("ack_topic", "Test cancel", 10*time.Second)

	go func() {
		time.Sleep(1 * time.Second)
		fmt.Println("🚫 Annulation de l'ACK...")
		ack5.Cancel()

		// Essayer d'attendre après cancel
		responses := ack5.Wait()
		fmt.Printf("📬 Réponses après cancel: %d (devrait être 0)\n", len(responses))
	}()

	time.Sleep(3 * time.Second)

	// Test 6: Comparaison Client vs Serveur ACK
	fmt.Println("\n6️⃣ Comparaison Client vs Serveur ACK")

	// Client ACK
	clientAck := testClient.PublishWithAck("ack_topic", "Client ACK", 3*time.Second)
	// Serveur ACK
	serverAck := testServer.PublishWithAck("ack_topic", "Serveur ACK", 3*time.Second)

	go func() {
		clientResp := clientAck.Wait()
		fmt.Printf("📱 Client ACK: %d réponses\n", len(clientResp))
	}()

	go func() {
		serverResp := serverAck.Wait()
		fmt.Printf("🌐 Serveur ACK: %d réponses\n", len(serverResp))
	}()

	time.Sleep(4 * time.Second)
	fmt.Println("\n✅ Tests ACK terminés!")
}
