# ManzAI Studio 開発工程書

## 開発ステップ4: Live2D統合とフロントエンド基盤の構築

### フロントエンドプロジェクトの初期設定

1. **Reactプロジェクトのセットアップ**
   ```bash
   # フロントエンドディレクトリに移動
   mkdir -p frontend
   cd frontend
   
   # package.jsonの作成
   cat > package.json << 'EOF'
   {
     "name": "manzai-studio-frontend",
     "version": "0.1.0",
     "private": true,
     "dependencies": {
       "@testing-library/jest-dom": "^5.17.0",
       "@testing-library/react": "^13.4.0",
       "@testing-library/user-event": "^13.5.0",
       "axios": "^1.6.2",
       "react": "^18.2.0",
       "react-dom": "^18.2.0",
       "react-scripts": "5.0.1",
       "web-vitals": "^2.1.4"
     },
     "scripts": {
       "start": "react-scripts start",
       "build": "react-scripts build",
       "test": "react-scripts test",
       "eject": "react-scripts eject"
     },
     "eslintConfig": {
       "extends": [
         "react-app",
         "react-app/jest"
       ]
     },
     "browserslist": {
       "production": [
         ">0.2%",
         "not dead",
         "not op_mini all"
       ],
       "development": [
         "last 1 chrome version",
         "last 1 firefox version",
         "last 1 safari version"
       ]
     },
     "proxy": "http://localhost:5000"
   }
   EOF
   
   # 依存パッケージのインストール
   npm install
   
   # 基本的なディレクトリ構造を作成
   mkdir -p src/components src/services src/assets public/live2d
   ```

2. **フロントエンドの基本構成ファイル作成**
   ```bash
   # index.htmlの作成
   cat > public/index.html << 'EOF'
   <!DOCTYPE html>
   <html lang="ja">
     <head>
       <meta charset="utf-8" />
       <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
       <meta name="viewport" content="width=device-width, initial-scale=1" />
       <meta name="theme-color" content="#000000" />
       <meta name="description" content="ManzAI Studio - ローカルで動作する漫才生成・実演Webアプリケーション" />
       <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
       <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
       <title>ManzAI Studio</title>
     </head>
     <body>
       <noscript>You need to enable JavaScript to run this app.</noscript>
       <div id="root"></div>
     </body>
   </html>
   EOF
   
   # index.jsの作成
   cat > src/index.js << 'EOF'
   import React from 'react';
   import ReactDOM from 'react-dom/client';
   import './index.css';
   import App from './App';
   import reportWebVitals from './reportWebVitals';
   
   const root = ReactDOM.createRoot(document.getElementById('root'));
   root.render(
     <React.StrictMode>
       <App />
     </React.StrictMode>
   );
   
   reportWebVitals();
   EOF
   
   # App.jsの作成
   cat > src/App.js << 'EOF'
   import React, { useState } from 'react';
   import './App.css';
   import ManzaiGenerator from './components/ManzaiGenerator';
   import Live2DStage from './components/Live2DStage';
   
   function App() {
     const [script, setScript] = useState([]);
     const [audioData, setAudioData] = useState([]);
     const [isLoading, setIsLoading] = useState(false);
     const [error, setError] = useState(null);
     
     return (
       <div className="App">
         <header className="App-header">
           <h1>ManzAI Studio</h1>
           <p>ローカルで動作する漫才生成・実演Webアプリケーション</p>
         </header>
         
         <main className="App-main">
           <div className="stage-container">
             <Live2DStage 
               script={script} 
               audioData={audioData} 
             />
           </div>
           
           <div className="control-container">
             <ManzaiGenerator 
               onScriptGenerated={(script, audioData) => {
                 setScript(script);
                 setAudioData(audioData);
               }}
               isLoading={isLoading}
               setIsLoading={setIsLoading}
               error={error}
               setError={setError}
             />
           </div>
         </main>
         
         <footer className="App-footer">
           <p>© 2025 ManzAI Studio</p>
         </footer>
       </div>
     );
   }
   
   export default App;
   EOF
   
   # スタイルシートの作成
   cat > src/App.css << 'EOF'
   .App {
     text-align: center;
     display: flex;
     flex-direction: column;
     min-height: 100vh;
   }
   
   .App-header {
     background-color: #282c34;
     padding: 20px;
     color: white;
   }
   
   .App-main {
     display: flex;
     flex-direction: column;
     flex-grow: 1;
     padding: 20px;
   }
   
   @media (min-width: 768px) {
     .App-main {
       flex-direction: row;
     }
   }
   
   .stage-container {
     flex: 2;
     min-height: 500px;
     position: relative;
     border: 1px solid #ddd;
     margin-bottom: 20px;
   }
   
   .control-container {
     flex: 1;
     padding: 0 20px;
   }
   
   .App-footer {
     background-color: #282c34;
     color: white;
     padding: 10px;
     margin-top: auto;
   }
   EOF
   
   # index.cssの作成
   cat > src/index.css << 'EOF'
   body {
     margin: 0;
     font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
       'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
       sans-serif;
     -webkit-font-smoothing: antialiased;
     -moz-osx-font-smoothing: grayscale;
   }
   
   code {
     font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
       monospace;
   }
   EOF
   
   # reportWebVitalsの作成
   cat > src/reportWebVitals.js << 'EOF'
   const reportWebVitals = onPerfEntry => {
     if (onPerfEntry && onPerfEntry instanceof Function) {
       import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
         getCLS(onPerfEntry);
         getFID(onPerfEntry);
         getFCP(onPerfEntry);
         getLCP(onPerfEntry);
         getTTFB(onPerfEntry);
       });
     }
   };
   
   export default reportWebVitals;
   EOF
   ```

### Live2D SDK の統合

1. **Live2D SDKのダウンロードと設定**
   ```bash
   # Live2D SDK用のディレクトリ作成
   mkdir -p public/live2d/Core
   
   # フロントエンド用のAPIサービスを作成
   cat > src/services/api.js << 'EOF'
   import axios from 'axios';

   const API_URL = '/api';
   
   export const generateManzai = async (topic) => {
     try {
       const response = await axios.post(`${API_URL}/generate`, { topic });
       return response.data;
     } catch (error) {
       console.error('Error generating manzai:', error);
       throw error;
     }
   };
   
   export const synthesizeScript = async (script, tsukkomiId = 1, bokeId = 3) => {
     try {
       const response = await axios.post(`${API_URL}/synthesize_script`, {
         script,
         tsukkomi_id: tsukkomiId,
         boke_id: bokeId
       });
       return response.data;
     } catch (error) {
       console.error('Error synthesizing script:', error);
       throw error;
     }
   };
   
   export const getSpeakers = async () => {
     try {
       const response = await axios.get(`${API_URL}/speakers`);
       return response.data;
     } catch (error) {
       console.error('Error getting speakers:', error);
       throw error;
     }
   };
   EOF
   ```

2. **Live2D SDK初期化用のユーティリティ作成**
   ```bash
   # Live2D初期化用のユーティリティを作成
   mkdir -p src/utils
   cat > src/utils/live2dInitializer.js << 'EOF'
   /**
    * Live2D初期化ユーティリティ
    */
   
   // Live2Dモデルを読み込み初期化する関数
   export const initializeLive2D = async (canvasId, modelPath) => {
     // Live2DがロードされているかチェックとWindow.Live2DCubismCoreがあるか確認
     if (!window.Live2DCubismCore) {
       console.error('Live2D Cubism Core is not loaded');
       return null;
     }
     
     try {
       // モデル定義ファイルをロード
       const response = await fetch(modelPath);
       const modelJson = await response.json();
       
       // キャンバス要素を取得
       const canvas = document.getElementById(canvasId);
       if (!canvas) {
         throw new Error(`Canvas element with id ${canvasId} not found`);
       }
       
       // Live2Dモデルの初期化コードを実装
       // 注: 実際の実装は公式SDKに従って行う必要があります
       
       // 仮のモデルオブジェクト
       const model = {
         setParameter: (name, value) => {
           console.log(`Setting parameter ${name} to ${value}`);
           // 実際にはモデルのパラメータを設定するコードを実装
         },
         update: () => {
           console.log('Updating model');
           // モデルの状態を更新するコードを実装
         },
         draw: () => {
           console.log('Drawing model');
           // モデルを描画するコードを実装
         }
       };
       
       return model;
     } catch (error) {
       console.error('Failed to initialize Live2D model:', error);
       return null;
     }
   };
   
   // 口の開閉を制御する関数
   export const updateMouth = (model, value) => {
     if (!model) return;
     
     // "ParamMouthOpenY"などの口の開閉を制御するパラメータを設定
     model.setParameter("ParamMouthOpenY", value);
     
     // モデルを更新して描画
     model.update();
     model.draw();
   };
   EOF
   ```

### キャラクター表示コンポーネントの作成

1. **Live2Dステージコンポーネントの作成**
   ```bash
   cat > src/components/Live2DStage.js << 'EOF'
   import React, { useEffect, useRef, useState } from 'react';
   import { initializeLive2D, updateMouth } from '../utils/live2dInitializer';
   
   const Live2DStage = ({ script, audioData }) => {
     const canvasRef = useRef(null);
     const [model, setModel] = useState(null);
     const [isPlaying, setIsPlaying] = useState(false);
     const [currentLine, setCurrentLine] = useState(0);
     const audioRef = useRef(null);
     const animationRef = useRef(null);
     
     // Live2Dモデルの初期化
     useEffect(() => {
       const initModel = async () => {
         // 本番では実際のモデルパスを指定
         const modelPath = '/live2d/models/sample/model.json';
         const initializedModel = await initializeLive2D('live2d-canvas', modelPath);
         if (initializedModel) {
           setModel(initializedModel);
         }
       };
       
       initModel();
       
       return () => {
         // クリーンアップ
         if (animationRef.current) {
           cancelAnimationFrame(animationRef.current);
         }
       };
     }, []);
     
     // 音声再生と口の動き同期
     useEffect(() => {
       if (!audioData || audioData.length === 0 || !model) return;
       
       const playSequence = () => {
         setIsPlaying(true);
         playLine(0);
       };
       
       const playLine = (index) => {
         if (index >= audioData.length) {
           setIsPlaying(false);
           setCurrentLine(-1);
           return;
         }
         
         setCurrentLine(index);
         const lineData = audioData[index];
         const audio = new Audio(lineData.audio_url);
         audioRef.current = audio;
         
         // 音声再生開始時の処理
         audio.onplay = () => {
           // リップシンクアニメーションの開始
           startLipSync(lineData.timing_data);
         };
         
         // 音声再生終了時の処理
         audio.onended = () => {
           // 口を閉じる
           updateMouth(model, 0);
           
           // 少し間を空けて次の行へ
           setTimeout(() => {
             playLine(index + 1);
           }, 500);
         };
         
         audio.play().catch(err => {
           console.error('Error playing audio:', err);
           playLine(index + 1);
         });
       };
       
       const startLipSync = (timingData) => {
         // タイミングデータを使用して口の動きを制御
         // 実際の実装ではモーラごとのタイミングを使って詳細な制御を行う
         let lastTime = 0;
         const accentPhrases = timingData?.accent_phrases || [];
         
         const animate = (timestamp) => {
           if (!audioRef.current) return;
           
           const currentTime = audioRef.current.currentTime * 1000; // ミリ秒に変換
           
           // 口の開閉状態をデフォルトで閉じた状態に
           let mouthOpenValue = 0;
           
           // アクセント句のモーラを順に確認
           for (const phrase of accentPhrases) {
             for (const mora of phrase.moras || []) {
               // 現在の再生時間がモーラの開始時間から終了時間の間にある場合
               if (currentTime >= mora.start_time && currentTime <= mora.end_time) {
                 // 母音の種類によって口の開き具合を調整
                 // 'a', 'o' -> 大きく開く, 'i', 'u', 'e' -> 小さく開く
                 const vowel = mora.vowel?.toLowerCase();
                 if (vowel === 'a' || vowel === 'o') {
                   mouthOpenValue = 1.0; // 大きく開く
                 } else if (vowel === 'i' || vowel === 'u') {
                   mouthOpenValue = 0.5; // 少し開く
                 } else if (vowel === 'e') {
                   mouthOpenValue = 0.7; // 中程度
                 } else {
                   mouthOpenValue = 0.3; // デフォルト
                 }
                 break;
               }
             }
           }
           
           // モデルの口の開閉を更新
           updateMouth(model, mouthOpenValue);
           
           // 次のフレームをリクエスト
           if (audioRef.current && !audioRef.current.paused) {
             animationRef.current = requestAnimationFrame(animate);
           }
         };
         
         // アニメーションの開始
         animationRef.current = requestAnimationFrame(animate);
       };
       
       // 再生ボタンを用意
       if (audioData.length > 0 && !isPlaying) {
         const playButton = document.createElement('button');
         playButton.textContent = '漫才を再生';
         playButton.className = 'play-button';
         playButton.onclick = playSequence;
         
         const container = canvasRef.current.parentElement;
         const existingButton = container.querySelector('.play-button');
         if (existingButton) {
           container.removeChild(existingButton);
         }
         container.appendChild(playButton);
       }
       
     }, [audioData, model, isPlaying]);
     
     return (
       <div className="live2d-container" style={{ position: 'relative', width: '100%', height: '100%' }}>
         <canvas
           id="live2d-canvas"
           ref={canvasRef}
           width="512"
           height="512"
           style={{ width: '100%', height: '100%' }}
         />
         
         {script && script.length > 0 && currentLine >= 0 && (
           <div className="dialogue-display" style={{
             position: 'absolute',
             bottom: '20px',
             left: '0',
             right: '0',
             background: 'rgba(0,0,0,0.7)',
             color: 'white',
             padding: '10px',
             borderRadius: '5px',
             margin: '0 auto',
             maxWidth: '80%',
             textAlign: 'center'
           }}>
             <p>
               <strong>{script[currentLine]?.speaker === 'tsukkomi' ? 'ツッコミ' : 'ボケ'}:</strong> {script[currentLine]?.text}
             </p>
           </div>
         )}
       </div>
     );
   };
   
   export default Live2DStage;
   EOF
   ```

2. **漫才生成フォームコンポーネントの作成**
   ```bash
   cat > src/components/ManzaiGenerator.js << 'EOF'
   import React, { useState, useEffect } from 'react';
   import { generateManzai, synthesizeScript, getSpeakers } from '../services/api';
   
   const ManzaiGenerator = ({ onScriptGenerated, isLoading, setIsLoading, error, setError }) => {
     const [topic, setTopic] = useState('');
     const [speakers, setSpeakers] = useState([]);
     const [tsukkomiId, setTsukkomiId] = useState(1); // デフォルト値
     const [bokeId, setBokeId] = useState(3); // デフォルト値
     
     // 話者一覧を取得
     useEffect(() => {
       const fetchSpeakers = async () => {
         try {
           const data = await getSpeakers();
           setSpeakers(data.speakers || []);
         } catch (err) {
           console.error('Failed to fetch speakers:', err);
           setError('話者一覧の取得に失敗しました。VoiceVoxが起動しているか確認してください。');
         }
       };
       
       fetchSpeakers();
     }, [setError]);
     
     const handleSubmit = async (e) => {
       e.preventDefault();
       if (!topic.trim()) {
         setError('トピックを入力してください');
         return;
       }
       
       setIsLoading(true);
       setError(null);
       
       try {
         // 1. 漫才台本の生成
         const scriptData = await generateManzai(topic);
         const script = scriptData.script;
         
         // 2. 音声の合成
         const audioData = await synthesizeScript(script, tsukkomiId, bokeId);
         
         // 親コンポーネントに結果を渡す
         onScriptGenerated(script, audioData.results);
       } catch (err) {
         console.error('Error in manzai generation process:', err);
         setError('漫才の生成中にエラーが発生しました。サーバーの状態を確認してください。');
       } finally {
         setIsLoading(false);
       }
     };
     
     return (
       <div className="manzai-generator">
         <h2>漫才生成</h2>
         
         <form onSubmit={handleSubmit}>
           <div className="form-group">
             <label htmlFor="topic">トピック:</label>
             <input
               type="text"
               id="topic"
               value={topic}
               onChange={(e) => setTopic(e.target.value)}
               disabled={isLoading}
               placeholder="例: スマートフォン、猫、旅行、etc..."
               className="form-control"
             />
           </div>
           
           <div className="form-group">
             <label htmlFor="tsukkomi">ツッコミ役の声:</label>
             <select
               id="tsukkomi"
               value={tsukkomiId}
               onChange={(e) => setTsukkomiId(Number(e.target.value))}
               disabled={isLoading || speakers.length === 0}
               className="form-control"
             >
               {speakers.map(speaker => (
                 <option key={speaker.id} value={speaker.id}>
                   {speaker.name}
                 </option>
               ))}
             </select>
           </div>
           
           <div className="form-group">
             <label htmlFor="boke">ボケ役の声:</label>
             <select
               id="boke"
               value={bokeId}
               onChange={(e) => setBokeId(Number(e.target.value))}
               disabled={isLoading || speakers.length === 0}
               className="form-control"
             >
               {speakers.map(speaker => (
                 <option key={speaker.id} value={speaker.id}>
                   {speaker.name}
                 </option>
               ))}
             </select>
           </div>
           
           <button
             type="submit"
             disabled={isLoading || !topic.trim()}
             className="submit-button"
           >
             {isLoading ? '生成中...' : '漫才を生成'}
           </button>
         </form>
         
         {error && <div className="error-message">{error}</div>}
         
         <div className="instructions">
           <h3>使い方</h3>
           <ol>
             <li>トピックを入力してください（例: 猫、旅行、スマートフォンなど）</li>
             <li>ツッコミ役とボケ役の声を選択してください</li>
             <li>「漫才を生成」ボタンをクリックしてください</li>
             <li>生成が完了したら、左側のステージで「漫才を再生」ボタンをクリックして鑑賞してください</li>
           </ol>
         </div>
       </div>
     );
   };
   
   export default ManzaiGenerator;
   EOF
   ```

### Live2Dモデルの仮データ設定

1. **サンプルLive2Dモデルディレクトリの作成**
   ```bash
   mkdir -p public/live2d/models/sample
   
   # サンプルモデル定義ファイルの作成
   cat > public/live2d/models/sample/model.json << 'EOF'
   {
     "version": "Sample 1.0.0",
     "model": "sample.moc3",
     "textures": [
       "sample.png"
     ],
     "pose": "sample.pose3.json",
     "physics": "sample.physics3.json",
     "motions": {
       "idle": [
         {
           "file": "sample_idle.motion3.json"
         }
       ]
     },
     "expressions": [
       {
         "name": "smile",
         "file": "sample_smile.exp3.json"
       }
     ]
   }
   EOF
   ```

2. **開発用のメモファイル作成**
   ```bash
   cat > DEVELOPMENT_NOTES.md << 'EOF'
   # 開発メモ

   ## Live2Dの実装について

   現在のLive2D実装はモックです。実際に動作させるためには以下の手順が必要です：

   1. Live2D Cubism SDK for Webのダウンロード
      - [Cubism SDK for Web](https://www.live2d.com/download/cubism-sdk/download-web/)からダウンロード
      - ダウンロードしたSDKのCoreディレクトリを `public/live2d/Core` にコピー

   2. 実際のLive2Dモデルの入手と配置
      - モデルファイルを `public/live2d/models/` 配下に配置
      - モデルパスを `Live2DStage.js` 内で正しく指定

   3. Live2D SDKを使った実装の完成
      - モデルのロード、描画、パラメータ制御の実装
      - リップシンクのより詳細な実装

   ## タスク

   - [ ] 実際のLive2D SDKのインストールと統合
   - [ ] サンプルモデルの入手と配置
   - [ ] リップシンク機能の詳細実装
   - [ ] キャラクター切り替え機能の実装
   EOF
   ```

### 開発サーバーの起動と統合テスト

1. **バックエンドとフロントエンドの起動スクリプト**
   ```bash
   cat > start_dev.sh << 'EOF'
   #!/bin/bash
   
   # バックエンドの起動
   echo "Starting backend server..."
   poetry run python -m flask --app backend/app/__init__.py run --debug &
   BACKEND_PID=$!
   
   # フロントエンドの起動
   echo "Starting frontend development server..."
   cd frontend && npm start &
   FRONTEND_PID=$!
   
   # プロセスを終了するための関数
   function cleanup {
     echo "Shutting down servers..."
     kill $BACKEND_PID
     kill $FRONTEND_PID
     exit
   }
   
   # Ctrl+Cでクリーンアップを実行
   trap cleanup INT
   
   # 待機
   wait
   EOF
   
   chmod +x start_dev.sh
   ```

2. **動作確認手順**
   ```bash
   # VoiceVoxとOllamaが起動していることを確認
   # Dockerを使用する場合
   docker-compose up -d
   
   # または直接サービスを起動
   # Ollamaの起動
   # VoiceVoxの起動（インストーラからGUIで起動）
   
   # 開発サーバーの起動
   ./start_dev.sh
   ```

この開発ステップでは、React.jsを使用したフロントエンドの基盤を構築し、Live2DキャラクターとVoiceVox音声合成を統合する初期実装を行いました。現時点ではLive2D部分はモック実装ですが、フロントエンドとバックエンドの統合、音声合成機能との連携の基本的な仕組みが整いました。次のステップでは、実際のLive2D SDK実装と、より高度な音声同期機能を実装します。