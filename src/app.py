from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from src.services.ollama_service import OllamaService
from src.services.voicevox_service import VoiceVoxService
from src.services.audio_manager import AudioManager
import os

def create_app():
    """Flaskアプリケーションを作成"""
    app = Flask(__name__)
    CORS(app)
    
    # サービスの初期化
    ollama_service = OllamaService()
    voicevox_service = VoiceVoxService()
    audio_manager = AudioManager()
    
    @app.route('/api/health')
    def health_check():
        """ヘルスチェックエンドポイント"""
        return jsonify({'status': 'healthy'})
    
    @app.route('/api/generate', methods=['POST'])
    def generate_manzai():
        """漫才生成エンドポイント"""
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 415
        
        data = request.get_json()
        topic = data.get('topic')
        
        if not topic:
            return jsonify({'error': 'topic is required'}), 400
        
        if topic == '':
            return jsonify({'error': 'topic cannot be empty'}), 400
        
        try:
            # 漫才スクリプトを生成
            script_data = ollama_service.generate_manzai_script(topic)
            
            # 音声を生成
            audio_data = []
            for line in script_data['script']:
                # 音声を生成
                voice_data = voicevox_service.generate_voice(
                    line['text'],
                    speaker_id=1 if line['role'] == 'tsukkomi' else 2
                )
                
                # 音声ファイルを保存
                filename = f"{line['role']}_{len(audio_data)}"
                audio_path = audio_manager.save_audio(voice_data, filename)
                
                audio_data.append({
                    'role': line['role'],
                    'audio_path': os.path.basename(audio_path)
                })
            
            return jsonify({
                'script': script_data['script'],
                'audio_data': audio_data
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/audio/<filename>')
    def get_audio(filename):
        """音声ファイル取得エンドポイント"""
        try:
            audio_data = audio_manager.get_audio(filename)
            return send_file(
                os.path.join(audio_manager.audio_dir, filename),
                mimetype='audio/wav'
            )
        except FileNotFoundError:
            return jsonify({'error': 'Audio file not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app 