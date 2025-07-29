package bus

import (
	"fmt"
	"os"
	"sync"
	"testing"
	"time"

	"github.com/kamalshkeir/ksmux"
)

var (
	testServer *ServerBus
	testClient *Client
)

// TestMain - Setup propre avec testing.M
func TestMain(m *testing.M) {
	// Setup: Démarrer UN SEUL serveur
	testServer = NewServer(ksmux.Config{
		Address: "localhost:8888",
	})

	go testServer.Run()
	time.Sleep(200 * time.Millisecond) // Attendre démarrage

	// Setup: Créer UN SEUL client
	var err error
	testClient, err = NewClient(ClientConnectOptions{
		Id:      "test-client",
		Address: "localhost:8888",
	})
	if err != nil {
		fmt.Printf("ERREUR CLIENT: %v\n", err)
		os.Exit(1)
	}

	time.Sleep(100 * time.Millisecond) // Attendre connexion

	// Lancer les tests
	code := m.Run()

	// Cleanup PROPRE
	testClient.Close()
	testServer.Stop() // Stop() ferme automatiquement le Bus

	os.Exit(code)
}

// Benchmark Subscribe WebSocket
func BenchmarkWebSocketSubscribe(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		unsub := testClient.Subscribe(fmt.Sprintf("topic-%d", i), func(data any, unsub func()) {
			// Callback simple
		})
		unsub() // Unsubscribe immédiatement
	}
}

// Benchmark Publish WebSocket
func BenchmarkWebSocketPublish(b *testing.B) {
	// Subscribe une fois
	testClient.Subscribe("bench-publish", func(data any, unsub func()) {
		// Callback simple
	})
	time.Sleep(50 * time.Millisecond)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		testClient.Publish("bench-publish", fmt.Sprintf("msg-%d", i))
	}
}

// Benchmark PublishToID WebSocket
func BenchmarkWebSocketPublishToID(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		testClient.PublishToID("server-id", fmt.Sprintf("direct-%d", i))
	}
}

// Benchmark Subscribe + Publish WebSocket
func BenchmarkWebSocketPubSub(b *testing.B) {
	var received int
	var mu sync.Mutex

	// Subscribe
	testClient.Subscribe("pubsub-bench", func(data any, unsub func()) {
		mu.Lock()
		received++
		mu.Unlock()
	})
	time.Sleep(50 * time.Millisecond)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		testClient.Publish("pubsub-bench", fmt.Sprintf("pubsub-%d", i))
	}
	b.StopTimer()

	// Attendre un peu pour les derniers messages
	time.Sleep(100 * time.Millisecond)

	mu.Lock()
	finalReceived := received
	mu.Unlock()

	b.Logf("Messages reçus: %d/%d", finalReceived, b.N)
}

// Benchmark ACK WebSocket
func BenchmarkWebSocketACK(b *testing.B) {
	// Subscribe pour ACK
	testClient.Subscribe("ack-bench", func(data any, unsub func()) {
		// Callback pour ACK
	})
	time.Sleep(50 * time.Millisecond)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ack := testServer.PublishWithAck("ack-bench", fmt.Sprintf("ack-%d", i), time.Millisecond*50)
		_ = ack // Pas d'attente pour éviter blocage
	}
}
