#!/usr/bin/env python3
"""
Script de setup rapide pour le client Python KPS (Ksmux Pub Sub) avec uv
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Exécute une commande et affiche le résultat"""
    print(f"🔧 {description}")
    print(f"   $ {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erreur: {e.stderr.strip()}")
        return False

def check_uv():
    """Vérifie que uv est installé"""
    try:
        result = subprocess.run("uv --version", shell=True, check=True, capture_output=True, text=True)
        print(f"✅ uv installé: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ uv n'est pas installé!")
        print("   Installer avec: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

def setup_project():
    """Setup complet du projet avec uv"""
    print("🚀 === SETUP KPS (KSMUX PUB SUB) PYTHON CLIENT AVEC UV ===\n")
    
    # Vérifier uv
    if not check_uv():
        return False
    
    # Créer l'environnement virtuel
    if not run_command("uv venv", "Création de l'environnement virtuel"):
        return False
    
    # Installer les dépendances principales
    if not run_command("uv pip install websockets orjson", "Installation des dépendances principales"):
        return False
    
    # Installer uvloop si pas sur Windows
    if sys.platform != "win32":
        if not run_command("uv pip install uvloop", "Installation de uvloop (Linux/macOS)"):
            print("   ⚠️ uvloop non installé, continuons sans...")
    
    # Installer les dépendances de dev
    if not run_command("uv pip install pytest pytest-asyncio black ruff mypy", "Installation des outils de dev"):
        return False
    
    print("\n✅ Setup terminé avec succès!")
    print("\n📋 Commandes utiles:")
    print("   🐍 Activer l'env:     source .venv/bin/activate  (Linux/macOS)")
    print("                        .venv\\Scripts\\activate     (Windows)")
    print("   🧪 Lancer les tests: python test_python_client.py")
    print("   🔧 Formater le code: uv run black .")
    print("   🔍 Linter:           uv run ruff check .")
    print("   📊 Type checking:    uv run mypy .")
    
    return True

def run_tests():
    """Lance les tests avec uv"""
    print("🧪 === LANCEMENT DES TESTS ===\n")
    
    if not run_command("uv run python test_python_client.py", "Lancement des tests"):
        return False
    
    print("\n✅ Tests terminés!")
    return True

def format_code():
    """Formate le code avec black"""
    print("🎨 === FORMATAGE DU CODE ===\n")
    
    if not run_command("uv run black .", "Formatage avec black"):
        return False
    
    if not run_command("uv run ruff check . --fix", "Linting avec ruff"):
        return False
    
    print("\n✅ Code formaté!")
    return True

def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        print("Usage: python setup.py [setup|test|format|all]")
        print("  setup  - Setup complet du projet")
        print("  test   - Lance les tests")
        print("  format - Formate le code")
        print("  all    - Fait tout")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        setup_project()
    elif command == "test":
        run_tests()
    elif command == "format":
        format_code()
    elif command == "all":
        if setup_project():
            format_code()
            run_tests()
    else:
        print(f"❌ Commande inconnue: {command}")

if __name__ == "__main__":
    main() 