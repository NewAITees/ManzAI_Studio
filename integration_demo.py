#!/usr/bin/env python3
"""
ManzAI Studio 統合デモンストレーション

スクリプト生成、音声合成、キャラクター動作の3つの機能を
同時に動かして動作を記録します。
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import requests


# ログ用の美しい出力
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_step(step_name: str, description: str = "") -> None:
    print(f"\n{Colors.CYAN}{'=' * 50}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}🚀 {step_name}{Colors.END}")
    if description:
        print(f"{Colors.YELLOW}   {description}{Colors.END}")
    print(f"{Colors.CYAN}{'=' * 50}{Colors.END}")


def print_success(message: str) -> None:
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message: str) -> None:
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_info(message: str) -> None:
    print(f"{Colors.PURPLE}ℹ️  {message}{Colors.END}")


def test_services() -> Dict[str, Any]:
    """基本サービスの接続テスト"""
    print_step("サービス接続テスト", "Ollama と VoiceVox の動作確認")

    services = {
        "Ollama": "http://localhost:11434/api/tags",
        "VoiceVox": "http://localhost:50021/version",
    }

    results: Dict[str, Any] = {}
    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                if service_name == "Ollama":
                    models = response.json().get("models", [])
                    print_success(f"{service_name}: {len(models)} models available")
                    results[service_name] = {"status": "ready", "models": len(models)}
                else:
                    version = response.text.strip('"')
                    print_success(f"{service_name}: v{version}")
                    results[service_name] = {"status": "ready", "version": version}
            else:
                print_error(f"{service_name}: HTTP {response.status_code}")
                results[service_name] = {"status": "error", "code": response.status_code}
        except Exception as e:
            print_error(f"{service_name}: {e!s}")
            results[service_name] = {"status": "error", "error": str(e)}

    return results


def generate_manzai_script(topic: str = "プログラミング") -> Dict[str, Any]:
    """漫才スクリプト生成のテスト"""
    print_step("スクリプト生成テスト", f"トピック: '{topic}' で漫才スクリプトを生成")

    # Ollamaを直接使用してスクリプト生成
    prompt = f"""
以下の形式で、「{topic}」をテーマにした漫才の台本を作成してください。

A: ツッコミ役
B: ボケ役

最低4つのやりとりを含めてください。

A: こんにちは、今日は{topic}について話しましょう。
B: よろしくお願いします！
"""

    try:
        # Ollamaに生成リクエスト
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "gemma3:4b", "prompt": prompt, "stream": False},
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            script_text = result.get("response", "")
            print_success(f"スクリプト生成完了 ({len(script_text)} 文字)")
            print_info("生成されたスクリプト:")
            print(f"{Colors.CYAN}{script_text[:300]}...{Colors.END}")
            return {"status": "success", "script": script_text[:500]}
        else:
            print_error(f"スクリプト生成失敗: HTTP {response.status_code}")
            return {"status": "error", "code": response.status_code}

    except Exception as e:
        print_error(f"スクリプト生成エラー: {e!s}")
        return {"status": "error", "error": str(e)}


def synthesize_voice(text: str = "こんにちは、今日は良い天気ですね。") -> Dict[str, Any]:
    """音声合成のテスト"""
    print_step("音声合成テスト", f"テキスト: '{text}' を音声に変換")

    try:
        # VoiceVoxで音声合成
        # まずは話者一覧を取得
        speakers_response = requests.get("http://localhost:50021/speakers", timeout=10)
        if speakers_response.status_code != 200:
            print_error(f"話者一覧取得失敗: HTTP {speakers_response.status_code}")
            return {"status": "error", "step": "speakers"}

        speakers = speakers_response.json()
        speaker_id = speakers[0]["styles"][0]["id"] if speakers else 1
        print_info(f"使用する話者ID: {speaker_id}")

        # 音声クエリ作成
        query_response = requests.post(
            "http://localhost:50021/audio_query",
            params={"text": text, "speaker": speaker_id},
            timeout=10,
        )

        if query_response.status_code != 200:
            print_error(f"音声クエリ作成失敗: HTTP {query_response.status_code}")
            return {"status": "error", "step": "query"}

        query_data = query_response.json()
        print_success("音声クエリ作成完了")

        # 音声合成実行
        synthesis_response = requests.post(
            "http://localhost:50021/synthesis",
            params={"speaker": speaker_id},
            json=query_data,
            timeout=15,
        )

        if synthesis_response.status_code == 200:
            audio_data = synthesis_response.content
            print_success(f"音声合成完了 ({len(audio_data)} bytes)")

            # 音声ファイル保存
            audio_dir = Path("demo_audio")
            audio_dir.mkdir(exist_ok=True)
            audio_file = audio_dir / f"demo_{int(time.time())}.wav"

            with open(audio_file, "wb") as f:
                f.write(audio_data)
            print_success(f"音声ファイル保存: {audio_file}")

            return {
                "status": "success",
                "file": str(audio_file),
                "size": len(audio_data),
                "speaker_id": speaker_id,
            }
        else:
            print_error(f"音声合成失敗: HTTP {synthesis_response.status_code}")
            return {"status": "error", "step": "synthesis"}

    except Exception as e:
        print_error(f"音声合成エラー: {e!s}")
        return {"status": "error", "error": str(e)}


def check_live2d_models() -> Dict[str, Any]:
    """Live2Dモデルファイルの確認"""
    print_step("Live2Dモデル確認", "利用可能なキャラクターモデルをチェック")

    models_dir = Path("frontend/public/live2d/models")
    if not models_dir.exists():
        print_error(f"Live2Dモデルディレクトリが見つかりません: {models_dir}")
        return {"status": "error", "error": "models directory not found"}

    models: List[Dict[str, Any]] = []
    for model_dir in models_dir.iterdir():
        if model_dir.is_dir() and model_dir.name != "default":
            model_file = None
            for pattern in ["*.model3.json", "*.model.json"]:
                model_files = list(model_dir.glob(pattern))
                if model_files:
                    model_file = model_files[0]
                    break

            if model_file:
                try:
                    with open(model_file, "r", encoding="utf-8") as f:
                        model_data = json.load(f)

                    # モーション数をカウント
                    motions_dir = model_dir / "motions"
                    motion_count = (
                        len(list(motions_dir.glob("*.motion3.json"))) if motions_dir.exists() else 0
                    )

                    textures = model_data.get("FileReferences", {}).get("Textures", [])
                    models.append(
                        {
                            "name": model_dir.name,
                            "file": model_file.name,
                            "motions": motion_count,
                            "textures": len(textures),
                        }
                    )
                    print_success(
                        f"✨ {model_dir.name}: {motion_count}モーション, {len(textures)}テクスチャ"
                    )
                except Exception as e:
                    print_error(f"❌ {model_dir.name}: {e!s}")

    if models:
        print_success(f"Live2Dモデル {len(models)}体が利用可能")
        return {"status": "success", "models": models}
    else:
        print_error("利用可能なLive2Dモデルが見つかりません")
        return {"status": "error", "error": "no models found"}


def full_integration_demo() -> Dict[str, Any]:
    """完全統合デモの実行"""
    print_step("統合デモ実行", "スクリプト生成 → 音声合成 → キャラクター確認")

    demo_results: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "services": {},
        "script": {},
        "voice": {},
        "live2d": {},
    }

    # 1. サービス確認
    print_info("Step 1: サービス接続確認")
    demo_results["services"] = test_services()

    # 2. スクリプト生成
    print_info("Step 2: 漫才スクリプト生成")
    demo_results["script"] = generate_manzai_script("AI開発")

    # 3. 音声合成（生成されたスクリプトの一部を使用）
    print_info("Step 3: 音声合成")
    if demo_results["script"].get("status") == "success":
        script_text = demo_results["script"].get("script", "")
        # スクリプトから最初の台詞を抽出
        lines = script_text.split("\n")
        voice_text = "AIについて話しましょう。"
        for line in lines:
            if line.strip() and (line.startswith("A:") or line.startswith("B:")):
                voice_text = line.split(":", 1)[1].strip()[:50]
                break
    else:
        voice_text = "こんにちは、今日は良い天気ですね。"

    demo_results["voice"] = synthesize_voice(voice_text)

    # 4. Live2Dモデル確認
    print_info("Step 4: Live2Dキャラクター確認")
    demo_results["live2d"] = check_live2d_models()

    # 5. 結果サマリー
    print_step("統合デモ結果", "全機能の動作状況")

    services_ok = all(s.get("status") == "ready" for s in demo_results["services"].values())
    script_ok = demo_results["script"].get("status") == "success"
    voice_ok = demo_results["voice"].get("status") == "success"
    live2d_ok = demo_results["live2d"].get("status") == "success"

    print(f"🔧 サービス接続: {'✅' if services_ok else '❌'}")
    print(f"📝 スクリプト生成: {'✅' if script_ok else '❌'}")
    print(f"🔊 音声合成: {'✅' if voice_ok else '❌'}")
    print(f"👤 Live2Dモデル: {'✅' if live2d_ok else '❌'}")

    overall_success = services_ok and script_ok and voice_ok and live2d_ok

    if overall_success:
        print_success("🎉 全機能が正常に動作しています！")
    else:
        print_error("⚠️  一部機能に問題があります")

    # 結果をファイルに保存
    results_file = Path("integration_demo_results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(demo_results, f, ensure_ascii=False, indent=2)
    print_info(f"詳細結果を保存: {results_file}")

    return demo_results


if __name__ == "__main__":
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("🎭 ManzAI Studio 統合デモンストレーション")
    print("=" * 60)
    print(f"{Colors.END}")

    try:
        results = full_integration_demo()

        print(f"\n{Colors.BOLD}{Colors.GREEN}")
        print("🏁 デモンストレーション完了")
        print("=" * 60)
        print(f"{Colors.END}")

        # 簡潔なサマリー表示
        print(f"実行時刻: {results['timestamp']}")
        ollama_models = results["services"].get("Ollama", {}).get("models", 0)
        print(f"Ollamaモデル: {ollama_models}個")
        voicevox_version = results["services"].get("VoiceVox", {}).get("version", "unknown")
        print(f"VoiceVoxバージョン: {voicevox_version}")
        live2d_models = results["live2d"].get("models", [])
        print(f"Live2Dモデル: {len(live2d_models)}体")

        if results["voice"].get("file"):
            print(f"生成音声: {results['voice']['file']}")

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}デモが中断されました{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"予期しないエラー: {e!s}")
        sys.exit(1)
