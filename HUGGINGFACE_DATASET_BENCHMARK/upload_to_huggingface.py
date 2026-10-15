#!/usr/bin/env python3
"""
Script interactivo para subir el dataset a Hugging Face usando huggingface_hub.
Uso:
    python3 upload_to_huggingface.py --repo-id <tu_usuario_hf>/qwen35-9b-gsm8k-benchmark --token <tu_token_hf>
O si ya iniciaste sesión con `hf auth login`:
    python3 upload_to_huggingface.py --repo-id <tu_usuario_hf>/qwen35-9b-gsm8k-benchmark
"""

import argparse
import sys
from pathlib import Path
from huggingface_hub import HfApi, create_repo

def main():
    parser = argparse.ArgumentParser(description="Subir dataset de benchmark sanitizado a Hugging Face.")
    parser.add_argument("--repo-id", type=str, required=True, help="Nombre del repositorio en HF (ej: tu_usuario/qwen35-9b-gsm8k-benchmark)")
    parser.add_argument("--token", type=str, default=None, help="Token de Hugging Face (con permisos de escritura). Si se omite, usa la sesión activa.")
    parser.add_argument("--private", action="store_true", help="Crear repositorio como privado (por defecto es público).")
    args = parser.parse_args()

    dataset_dir = Path(__file__).parent.resolve()
    print(f"📦 Directorio a subir: {dataset_dir}")
    print(f"🎯 Repositorio destino: {args.repo_id} (tipo: dataset)")

    api = HfApi(token=args.token)

    try:
        print("🔍 Verificando / creando repositorio en Hugging Face...")
        create_repo(
            repo_id=args.repo_id,
            repo_type="dataset",
            private=args.private,
            exist_ok=True,
            token=args.token,
        )
        print("✅ Repositorio listo en Hugging Face.")

        print("🚀 Subiendo archivos del dataset (esto puede tomar 1 o 2 minutos)...")
        api.upload_folder(
            folder_path=str(dataset_dir),
            repo_id=args.repo_id,
            repo_type="dataset",
            ignore_patterns=["upload_to_huggingface.py", "__pycache__", ".git*"],
        )
        print(f"\n🎉 ¡Subida completada con éxito!")
        print(f"🌐 Ver en Hugging Face: https://huggingface.co/datasets/{args.repo_id}")

    except Exception as e:
        print(f"❌ Error durante la subida: {e}")
        print("\nSugerencia: Asegúrate de tener una sesión activa con `hf auth login` o pasar tu token con `--token hf_...`")
        sys.exit(1)

if __name__ == "__main__":
    main()
