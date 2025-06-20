#!/usr/bin/env python3
"""
Simple server launcher for ManzAI Studio backend
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.backend.app import create_app  # noqa: E402


def main() -> None:
    """Start the Flask development server"""
    # Set environment variables for development
    os.environ["FLASK_ENV"] = "development"
    os.environ["FLASK_DEBUG"] = "1"

    # Create the Flask app
    app = create_app()

    print("🚀 Starting ManzAI Studio Backend Server...")
    print("📍 Server URL: http://localhost:5000")
    print("🏥 Health Check: http://localhost:5000/api/health")
    print("📊 Status: http://localhost:5000/api/detailed-status")
    print("🎭 Generate: POST http://localhost:5000/api/generate")
    print("🔊 Speakers: http://localhost:5000/api/speakers")
    print("\n📋 Available API Endpoints:")
    print("  GET  /api/health              - Health check")
    print("  GET  /api/detailed-status     - Detailed system status")
    print("  POST /api/generate            - Generate manzai script")
    print("  GET  /api/speakers            - List VoiceVox speakers")
    print("  GET  /api/audio/<filename>    - Get audio file")
    print("  GET  /api/audio/list          - List audio files")
    print("  POST /api/audio/cleanup       - Cleanup old audio files")
    print("  POST /api/timing              - Get lip sync timing data")
    print("\n💡 Test with mock data:")
    print("  curl -X POST http://localhost:5000/api/generate \\")
    print('       -H "Content-Type: application/json" \\')
    print('       -d \'{"topic": "テスト", "use_mock": true}\'')
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)

    try:
        # Run the Flask development server
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True,
            use_reloader=False,  # Disable reloader to avoid double startup
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")


if __name__ == "__main__":
    main()
