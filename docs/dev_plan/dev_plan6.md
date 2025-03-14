# ManzAI Studio 開発工程書

## 開発ステップ6: キャラクター切り替え機能とエラーハンドリングの強化

### キャラクター管理システムの実装

1. **キャラクター管理ストアの作成**
   ```bash
   # キャラクター情報を管理するストアを作成
   mkdir -p frontend/src/stores
   cat > frontend/src/stores/characterStore.js << 'EOF'
   /**
    * キャラクター管理ストア
    */
   import { useState, useEffect, createContext, useContext } from 'react';
   import { LIVE2D_MODELS } from '../config';
   
   // キャラクターコンテキストの作成
   export const CharacterContext = createContext(null);
   
   // キャラクター情報の初期値
   const initialCharacters = {
     tsukkomi: {
       id: 'tsukkomi_1',
       name: 'ツッコミ役',
       modelPath: LIVE2D_MODELS.TSUKKOMI.path,
       speakerId: 1, // VoiceVoxの話者ID
       active: true,
     },
     boke: {
       id: 'boke_1',
       name: 'ボケ役',
       modelPath: LIVE2D_MODELS.BOKE.path,
       speakerId: 3, // VoiceVoxの話者ID
       active: true,
     }
   };
   
   // ローカルストレージから既存のキャラクター情報を読み込む
   const loadSavedCharacters = () => {
     try {
       const saved = localStorage.getItem('manzai_characters');
       return saved ? JSON.parse(saved) : initialCharacters;
     } catch (error) {
       console.error('Failed to load saved characters:', error);
       return initialCharacters;
     }
   };
   
   // キャラクター管理フックの作成
   export const useCharacterStore = () => {
     const [characters, setCharacters] = useState(loadSavedCharacters);
     const [activeCharacter, setActiveCharacter] = useState('tsukkomi');
     const [availableModels, setAvailableModels] = useState([]);
     
     // 利用可能なモデル一覧の読み込み
     useEffect(() => {
       // 本来はAPIから取得するが、今回はモックデータを使用
       const mockModels = [
         {
           id: 'tsukkomi_1',
           name: 'ツッコミ役 (標準)',
           path: LIVE2D_MODELS.TSUKKOMI.path,
           type: 'tsukkomi'
         },
         {
           id: 'boke_1',
           name: 'ボケ役 (標準)',
           path: LIVE2D_MODELS.BOKE.path,
           type: 'boke'
         }
       ];
       
       setAvailableModels(mockModels);
     }, []);
     
     // キャラクター情報を更新してローカルストレージに保存
     const updateCharacter = (type, data) => {
       const updatedCharacters = {
         ...characters,
         [type]: {
           ...characters[type],
           ...data
         }
       };
       
       setCharacters(updatedCharacters);
       
       // ローカルストレージに保存
       try {
         localStorage.setItem('manzai_characters', JSON.stringify(updatedCharacters));
       } catch (error) {
         console.error('Failed to save characters:', error);
       }
     };
     
     // キャラクターモデルを変更
     const changeCharacterModel = (type, modelId) => {
       const model = availableModels.find(m => m.id === modelId);
       if (model) {
         updateCharacter(type, {
           id: modelId,
           modelPath: model.path
         });
       }
     };
     
     // 話者IDを変更
     const changeSpeakerId = (type, speakerId) => {
       updateCharacter(type, { speakerId: Number(speakerId) });
     };
     
     // アクティブキャラクターを切り替え
     const switchActiveCharacter = (type) => {
       setActiveCharacter(type);
     };
     
     return {
       characters,
       activeCharacter,
       availableModels,
       changeCharacterModel,
       changeSpeakerId,
       switchActiveCharacter
     };
   };
   
   // キャラクター管理プロバイダーコンポーネント
   export const CharacterProvider = ({ children }) => {
     const characterStore = useCharacterStore();
     
     return (
       <CharacterContext.Provider value={characterStore}>
         {children}
       </CharacterContext.Provider>
     );
   };
   
   // キャラクターフックの使用ヘルパー
   export const useCharacters = () => useContext(CharacterContext);
   EOF
   ```

2. **キャラクター切り替えコンポーネントの作成**
   ```bash
   # キャラクター切り替えコンポーネントを作成
   cat > frontend/src/components/CharacterSelector.js << 'EOF'
   import React from 'react';
   import { useCharacters } from '../stores/characterStore';
   
   const CharacterSelector = ({ speakers = [], disabled = false }) => {
     const {
       characters,
       activeCharacter,
       availableModels,
       changeCharacterModel,
       changeSpeakerId,
       switchActiveCharacter
     } = useCharacters();
     
     return (
       <div className="character-selector">
         <div className="character-tabs">
           <button
             className={`character-tab ${activeCharacter === 'tsukkomi' ? 'active' : ''}`}
             onClick={() => switchActiveCharacter('tsukkomi')}
             disabled={disabled}
           >
             ツッコミ役
           </button>
           <button
             className={`character-tab ${activeCharacter === 'boke' ? 'active' : ''}`}
             onClick={() => switchActiveCharacter('boke')}
             disabled={disabled}
           >
             ボケ役
           </button>
         </div>
         
         <div className="character-settings">
           <div className="form-group">
             <label htmlFor="character-model">キャラクターモデル:</label>
             <select
               id="character-model"
               value={characters[activeCharacter].id}
               onChange={(e) => changeCharacterModel(activeCharacter, e.target.value)}
               disabled={disabled}
               className="form-control"
             >
               {availableModels
                 .filter(model => model.type === activeCharacter)
                 .map(model => (
                   <option key={model.id} value={model.id}>
                     {model.name}
                   </option>
                 ))}
             </select>
           </div>
           
           <div className="form-group">
             <label htmlFor="character-voice">キャラクターボイス:</label>
             <select
               id="character-voice"
               value={characters[activeCharacter].speakerId}
               onChange={(e) => changeSpeakerId(activeCharacter, e.target.value)}
               disabled={disabled || speakers.length === 0}
               className="form-control"
             >
               {speakers.map(speaker => (
                 <option key={speaker.id} value={speaker.id}>
                   {speaker.name}
                 </option>
               ))}
             </select>
           </div>
         </div>
         
         <style jsx>{`
           .character-selector {
             margin-bottom: 20px;
             border: 1px solid #ddd;
             border-radius: 5px;
             overflow: hidden;
           }
           
           .character-tabs {
             display: flex;
             border-bottom: 1px solid #ddd;
           }
           
           .character-tab {
             flex: 1;
             padding: 10px;
             background: none;
             border: none;
             cursor: pointer;
             text-align: center;
             font-weight: bold;
             transition: background-color 0.2s;
           }
           
           .character-tab.active {
             background-color: #3498db;
             color: white;
           }
           
           .character-tab:hover:not(.active):not(:disabled) {
             background-color: #f0f0f0;
           }
           
           .character-tab:disabled {
             cursor: not-allowed;
             opacity: 0.6;
           }
           
           .character-settings {
             padding: 15px;
           }
         `}</style>
       </div>
     );
   };
   
   export default CharacterSelector;
   EOF
   ```

3. **アプリケーションにキャラクター管理を統合**
   ```bash
   # App.jsを更新してプロバイダーを統合
   cat > frontend/src/App.js << 'EOF'
   import React, { useState } from 'react';
   import './App.css';
   import ManzaiGenerator from './components/ManzaiGenerator';
   import Live2DStage from './components/Live2DStage';
   import { CharacterProvider } from './stores/characterStore';
   
   function App() {
     const [script, setScript] = useState([]);
     const [audioData, setAudioData] = useState([]);
     const [isLoading, setIsLoading] = useState(false);
     const [error, setError] = useState(null);
     
     return (
       <CharacterProvider>
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
       </CharacterProvider>
     );
   }
   
   export default App;
   EOF
   ```

### Live2Dステージコンポーネントの改良

1. **キャラクター切り替えに対応したLive2Dステージ**
   ```bash
   # キャラクター切り替えに対応したLive2Dステージコンポーネントを作成
   cat > frontend/src/components/Live2DStage.js << 'EOF'
   import React, { useEffect, useRef, useState, useCallback } from 'react';
   import { initializeLive2D, updateMouth, releaseLive2D } from '../utils/live2dInitializer';
   import { useCharacters } from '../stores/characterStore';
   
   const Live2DStage = ({ script, audioData }) => {
     const { characters } = useCharacters();
     const canvasRef = useRef(null);
     const [live2dInstances, setLive2dInstances] = useState({
       tsukkomi: null,
       boke: null
     });
     const [isPlaying, setIsPlaying] = useState(false);
     const [currentLine, setCurrentLine] = useState(-1);
     const audioRef = useRef(null);
     const animationFrameRef = useRef(null);
     
     // キャラクターの初期位置設定
     const characterPositions = {
       tsukkomi: { x: -150, y: 0 }, // 左
       boke: { x: 150, y: 0 }       // 右
     };
     
     // Live2Dモデルの初期化
     useEffect(() => {
       const initModels = async () => {
         try {
           // キャンバスが存在することを確認
           if (!canvasRef.current) return;
           
           // 既存のインスタンスをクリーンアップ
           Object.values(live2dInstances).forEach(instance => {
             if (instance) releaseLive2D(instance);
           });
           
           // 新しいインスタンスを初期化
           const newInstances = { tsukkomi: null, boke: null };
           
           // ツッコミ役モデルの初期化
           const tsukkomiInstance = await initializeLive2D(
             'live2d-canvas', 
             characters.tsukkomi.modelPath,
             characterPositions.tsukkomi
           );
           
           if (tsukkomiInstance) {
             console.log('Tsukkomi model initialized');
             newInstances.tsukkomi = tsukkomiInstance;
             tsukkomiInstance.lipSyncController.start();
           }
           
           // ボケ役モデルの初期化
           const bokeInstance = await initializeLive2D(
             'live2d-canvas', 
             characters.boke.modelPath,
             characterPositions.boke
           );
           
           if (bokeInstance) {
             console.log('Boke model initialized');
             newInstances.boke = bokeInstance;
             bokeInstance.lipSyncController.start();
           }
           
           setLive2dInstances(newInstances);
         } catch (error) {
           console.error('Error initializing Live2D models:', error);
         }
       };
       
       initModels();
       
       // クリーンアップ
       return () => {
         if (animationFrameRef.current) {
           cancelAnimationFrame(animationFrameRef.current);
         }
         
         Object.values(live2dInstances).forEach(instance => {
           if (instance) releaseLive2D(instance);
         });
       };
     }, [characters.tsukkomi.modelPath, characters.boke.modelPath]);
     
     // モーラデータから口の開き具合を計算
     const calculateMouthOpenValue = useCallback((currentTime, timingData) => {
       const accentPhrases = timingData?.accent_phrases || [];
       
       // 口の開閉状態をデフォルトで閉じた状態に
       let mouthOpenValue = 0;
       
       // アクセント句のモーラを順に確認
       for (const phrase of accentPhrases) {
         for (const mora of phrase.moras || []) {
           // 現在の再生時間がモーラの開始時間から終了時間の間にある場合
           if (currentTime >= mora.start_time && currentTime <= mora.end_time) {
             // 母音の種類によって口の開き具合を調整
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
             return mouthOpenValue;
           }
         }
       }
       
       return mouthOpenValue;
     }, []);
     
     // リップシンクアニメーションを開始
     const startLipSync = useCallback((audio, timingData, speakerType) => {
       if (!live2dInstances[speakerType]) return;
       
       // 他のモデルの口を閉じる
       Object.entries(live2dInstances).forEach(([type, instance]) => {
         if (type !== speakerType && instance) {
           updateMouth(instance, 0);
         }
       });
       
       const animate = () => {
         if (!audio || audio.paused || audio.ended) {
           updateMouth(live2dInstances[speakerType], 0);
           cancelAnimationFrame(animationFrameRef.current);
           return;
         }
         
         const currentTime = audio.currentTime * 1000; // ミリ秒に変換
         const mouthOpenValue = calculateMouthOpenValue(currentTime, timingData);
         
         updateMouth(live2dInstances[speakerType], mouthOpenValue);
         
         animationFrameRef.current = requestAnimationFrame(animate);
       };
       
       // アニメーションの開始
       animationFrameRef.current = requestAnimationFrame(animate);
     }, [live2dInstances, calculateMouthOpenValue]);
     
     // 音声再生とリップシンク
     useEffect(() => {
       if (!audioData || audioData.length === 0 || 
           !live2dInstances.tsukkomi || !live2dInstances.boke) return;
       
       // 漫才再生シーケンス
       const playSequence = () => {
         setIsPlaying(true);
         playLine(0);
       };
       
       // 1行ずつ再生
       const playLine = (index) => {
         if (index >= audioData.length) {
           setIsPlaying(false);
           setCurrentLine(-1);
           
           // 両方のキャラクターの口を閉じる
           updateMouth(live2dInstances.tsukkomi, 0);
           updateMouth(live2dInstances.boke, 0);
           return;
         }
         
         setCurrentLine(index);
         const lineData = audioData[index];
         const speakerType = lineData.speaker === 'tsukkomi' ? 'tsukkomi' : 'boke';
         const audio = new Audio(lineData.audio_url);
         audioRef.current = audio;
         
         // 音声再生開始時の処理
         audio.onplay = () => {
           startLipSync(audio, lineData.timing_data, speakerType);
         };
         
         // 音声再生終了時の処理
         audio.onended = () => {
           // 口を閉じる
           updateMouth(live2dInstances[speakerType], 0);
           
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
       
       // 再生ボタンを用意
       if (audioData.length > 0 && !isPlaying) {
         const container = canvasRef.current?.parentElement;
         if (!container) return;
         
         const existingButton = container.querySelector('.play-button');
         if (existingButton) {
           container.removeChild(existingButton);
         }
         
         const playButton = document.createElement('button');
         playButton.textContent = '漫才を再生';
         playButton.className = 'play-button';
         playButton.style.position = 'absolute';
         playButton.style.bottom = '80px';
         playButton.style.left = '50%';
         playButton.style.transform = 'translateX(-50%)';
         playButton.style.padding = '10px 20px';
         playButton.style.fontSize = '16px';
         playButton.style.backgroundColor = '#4CAF50';
         playButton.style.color = 'white';
         playButton.style.border = 'none';
         playButton.style.borderRadius = '5px';
         playButton.style.cursor = 'pointer';
         playButton.style.zIndex = '100';
         playButton.onclick = playSequence;
         
         container.appendChild(playButton);
       }
       
     }, [audioData, live2dInstances, isPlaying, startLipSync]);
     
     return (
       <div className="live2d-container" style={{ position: 'relative', width: '100%', height: '100%' }}>
         <canvas
           id="live2d-canvas"
           ref={canvasRef}
           width="800"
           height="600"
           style={{ width: '100%', height: '100%', background: 'linear-gradient(to bottom, #e6f7ff, #f2f2f2)' }}
         />
         
         {script && script.length > 0 && currentLine >= 0 && currentLine < script.length && (
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

2. **Live2D初期化ユーティリティの更新**
   ```bash
   # 位置情報を追加したLive2D初期化関数を更新
   cat > frontend/src/utils/live2dInitializer.js << 'EOF'
   /**
    * Live2D初期化ユーティリティ
    */
   
   // Live2Dモデルローダー
   export class Live2DModelLoader {
     constructor(canvasId, position = { x: 0, y: 0 }) {
       this.canvas = document.getElementById(canvasId);
       this.gl = this.canvas.getContext('webgl');
       this.model = null;
       this.modelMatrix = null;
       this.viewMatrix = null;
       this.projectionMatrix = null;
       this.animator = null;
       this.physics = null;
       this.renderer = null;
       this.startTime = Date.now();
       this.frameCount = 0;
       this.isLostContext = false;
       this.rafId = null;
       this.position = position;
       
       // WebGLコンテキストの消失イベントのハンドリング
       this.canvas.addEventListener('webglcontextlost', this.handleContextLost.bind(this));
       this.canvas.addEventListener('webglcontextrestored', this.handleContextRestored.bind(this));
     }
     
     async loadModel(modelPath) {
       if (!window.Live2DCubismCore) {
         console.error('Live2D Cubism Core is not loaded');
         return false;
       }
       
       try {
         // モデル定義をフェッチ
         const response = await fetch(modelPath);
         const modelDefinition = await response.json();
         
         // モデルのディレクトリパスを取得
         const modelDir = modelPath.substring(0, modelPath.lastIndexOf('/') + 1);
         
         // モックファイルのパス
         const mocPath = modelDir + modelDefinition.model;
         
         // モックファイルをフェッチ
         const mocResponse = await fetch(mocPath);
         const mocArrayBuffer = await mocResponse.arrayBuffer();
         
         // Live2D Cubism Frameworkの初期化
         window.Live2DCubismFramework.CubismStartup();
         
         // モデルの作成と初期化
         const moc = window.Live2DCubismFramework.CubismMoc.create(mocArrayBuffer);
         this.model = window.Live2DCubismFramework.CubismModel.create(moc);
         
         // テクスチャのロード
         const textureInfo = [];
         for (let i = 0; i < modelDefinition.textures.length; i++) {
           const texturePath = modelDir + modelDefinition.textures[i];
           const texture = await this.createTexture(texturePath);
           textureInfo.push({ texture });
         }
         
         // レンダラの初期化
         this.renderer = window.Live2DCubismFramework.CubismRenderer.create();
         this.renderer.initialize(this.model);
         this.renderer.setIsPremultipliedAlpha(true);
         this.renderer.setRenderState(this.gl, 0, 0, this.canvas.width, this.canvas.height);
         this.renderer.setTextures(textureInfo);
         
         // モデル行列の設定 - 位置情報を適用
         this.modelMatrix = new window.Live2DCubismFramework.CubismMatrix44();
         this.modelMatrix.scale(1.0, 1.0);
         this.modelMatrix.translateX(this.position.x / this.canvas.width);
         this.modelMatrix.translateY(this.position.y / this.canvas.height);
         
         // 描画ループの開始
         this.startRenderLoop();
         
         return true;
       } catch (error) {
         console.error('Failed to load Live2D model:', error);
         return false;
       }
     }
     
     // 残りのメソッドは以前のバージョンと同じ
     // ...
   }
   
   // Live2Dモデルとコントローラのインスタンスを作成して公開
   export const initializeLive2D = async (canvasId, modelPath, position = { x: 0, y: 0 }) => {
     try {
       const modelLoader = new Live2DModelLoader(canvasId, position);
       const success = await modelLoader.loadModel(modelPath);
       
       if (success) {
         const lipSyncController = new LipSyncController(modelLoader);
         return {
           modelLoader,
           lipSyncController
         };
       }
       
       return null;
     } catch (error) {
       console.error('Failed to initialize Live2D:', error);
       return null;
     }
   };
   
   // 残りの関数は以前のバージョンと同じ
   // ...
   EOF
   ```

### 漫才生成フォームの更新

1. **キャラクター切り替えを統合した漫才生成フォーム**
   ```bash
   # ManzaiGeneratorコンポーネントを更新
   cat > frontend/src/components/ManzaiGenerator.js << 'EOF'
   import React, { useState, useEffect } from 'react';
   import { generateManzai, synthesizeScript, getSpeakers } from '../services/api';
   import LoadingSpinner from './ui/LoadingSpinner';
   import CharacterSelector from './CharacterSelector';
   import { useCharacters } from '../stores/characterStore';
   
   const ManzaiGenerator = ({ onScriptGenerated, isLoading, setIsLoading, error, setError }) => {
     const { characters } = useCharacters();
     const [topic, setTopic] = useState('');
     const [speakers, setSpeakers] = useState([]);
     const [loadingPhase, setLoadingPhase] = useState('');
     const [generationProgress, setGenerationProgress] = useState(0);
     
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
       setGenerationProgress(0);
       
       try {
         // 1. 漫才台本の生成
         setLoadingPhase('台本を生成中...');
         setGenerationProgress(10);
         const scriptData = await generateManzai(topic);
         const script = scriptData.script;
         setGenerationProgress(40);
         
         // 2. 音声の合成
         setLoadingPhase('音声を合成中...');
         setGenerationProgress(60);
         const audioData = await synthesizeScript(
           script, 
           characters.tsukkomi.speakerId, 
           characters.boke.speakerId
         );
         setGenerationProgress(90);
         
         // シリアライズが完了するまで少し待つ
         setTimeout(() => {
           setGenerationProgress(100);
           
           // 3. 親コンポーネントに結果を渡す
           onScriptGenerated(script, audioData.results);
           
           setIsLoading(false);
           setLoadingPhase('');
         }, 500);
       } catch (err) {
         console.error('Error in manzai generation process:', err);
         
         // エラー処理の改善
         let errorMessage = '漫才の生成中にエラーが発生しました。';
         
         if (err.response) {
           // サーバーからのエラーレスポンス
           if (err.response.status === 500) {
             errorMessage += ' サーバー内部エラーが発生しました。';
           } else if (err.response.status === 404) {
             errorMessage += ' APIが見つかりません。';
           } else if (err.response.data && err.response.data.error) {
             errorMessage += ` ${err.response.data.error}`;
           }
         } else if (err.request) {
           // リクエストは送信されたがレスポンスがない
           errorMessage += ' サーバーに接続できません。Ollamaサーバーが起動しているか確認してください。';
         } else {
           // リクエスト設定中のエラー
           errorMessage += ` ${err.message}`;
         }
         
         setError(errorMessage);
         setIsLoading(false);
         setLoadingPhase('');
       }
     };
     
     // 漫才のサンプルトピック
     const sampleTopics = [
       'スマートフォン', '旅行', '猫', '料理', 'スポーツ', '音楽', '読書', '映画', '季節', '天気'
     ];
     
     const handleSampleTopicClick = (topic) => {
       setTopic(topic);
     };
     
     return (
       <div className="manzai-generator">
         <h2>漫才生成</h2>
         
         {isLoading ? (
           <div className="loading-container">
             <LoadingSpinner text={loadingPhase} />
             <div className="progress-bar-container">
               <div 
                 className="progress-bar" 
                 style={{ width: `${generationProgress}%` }}
               />
             </div>
             <div className="progress-text">
               {generationProgress}%
             </div>
           </div>
         ) : (
           <>
             <CharacterSelector 
               speakers={speakers} 
               disabled={isLoading} 
             />
             
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
                 <div className="sample-topics">
                   <p>サンプルトピック: </p>
                   <div className="topic-tags">
                     {sampleTopics.map((sampleTopic) => (
                       <span 
                         key={sampleTopic} 
                         className="topic-tag"
                         onClick={() => handleSampleTopicClick(sampleTopic)}
                       >
                         {sampleTopic}
                       </span>
                     ))}
                   </div>
                 </div>
               </div>
               
               <button
                 type="submit"
                 disabled={isLoading || !topic.trim()}
                 className="submit-button"
               >
                 漫才を生成
               </button>
             </form>
             
             {error && <div className="error-message">{error}</div>}
             
             <div className="instructions">
               <h3>使い方</h3>
               <ol>
                 <li>キャラクターの設定を確認・変更します</li>
                 <li>トピックを入力します（例: 猫、旅行、スマートフォンなど）</li>
                 <li>「漫才を生成」ボタンをクリックします</li>
                 <li>生成が完了したら、ステージ上の「漫才を再生」ボタンをクリックして鑑賞します</li>
               </ol>
             </div>
           </>
         )}
         
         <style jsx>{`
           .loading-container {
             display: flex;
             flex-direction: column;
             align-items: center;
             padding: 30px 0;
           }
           
           .progress-bar-container {
             width: 100%;
             height: 10px;
             background-color: #f0f0f0;
             border-radius: 5px;
             margin: 10px 0;
             overflow: hidden;
           }
           
           .progress-bar {
             height: 100%;
             background-color: #3498db;
             transition: width 0.3s ease;
           }
           
           .progress-text {
             font-size: 14px;
             color: #666;
           }
           
           .sample-topics {
             margin-top: 10px;
             text-align: left;
           }
           
           .sample-topics p {
             margin-bottom: 5px;
             font-size: 14px;
             color: #666;
           }
           
           .topic-tags {
             display: flex;
             flex-wrap: wrap;
             gap: 8px;
           }
           
           .topic-tag {
             background-color: #f0f0f0;
             padding: 5px 10px;
             border-radius: 15px;
             font-size: 13px;
             cursor: pointer;
             transition: background-color 0.2s;
           }
           
           .topic-tag:hover {
             background-color: #e0e0e0;
           }
         `}</style>
       </div>
     );
   };
   
   export default ManzaiGenerator;
   EOF
   ```

### エラーハンドリングの強化

1. **バックエンドのエラーハンドリング改善**
   ```bash
   # バックエンドのエラーハンドリング改善
   cat > src/backend/app/utils/error_handlers.py << 'EOF'
   """エラーハンドリングユーティリティ"""
   from flask import jsonify
   from functools import wraps
   import logging
   
   logger = logging.getLogger(__name__)
   
   class APIError(Exception):
       """API用カスタムエラー"""
       def __init__(self, message, status_code=400, payload=None):
           super().__init__()
           self.message = message
           self.status_code = status_code
           self.payload = payload
   
       def to_dict(self):
           """エラー情報を辞書形式で返す"""
           rv = dict(self.payload or ())
           rv['error'] = self.message
           return rv
   
   def handle_api_error(error):
       """APIエラーハンドラ"""
       response = jsonify(error.to_dict())
       response.status_code = error.status_code
       return response
   
   def api_error_handler(f):
       """API関数用のエラーハンドリングデコレータ"""
       @wraps(f)
       def decorated_function(*args, **kwargs):
           try:
               return f(*args, **kwargs)
           except APIError as e:
               return handle_api_error(e)
           except Exception as e:
               logger.exception("Unhandled exception in API route")
               error = APIError(
                   message=f"サーバーエラーが発生しました: {str(e)}",
                   status_code=500
               )
               return handle_api_error(error)
       return decorated_function
   EOF
   ```

2. **APIルートにエラーハンドリングを適用**
   ```bash
   # APIルートにエラーハンドリングを統合
   cat > src/backend/app/routes/api.py << 'EOF'
   """API routes for the backend application."""
   from flask import Blueprint, jsonify, request, current_app
   from typing import Dict, Any
   import os
   import requests
   
   from backend.app.services.ollama_service import OllamaService
   from backend.app.services.voicevox_service import VoiceVoxService
   from backend.app.utils.prompt_loader import load_prompt
   from backend.app.utils.error_handlers import api_error_handler, APIError
   
   bp = Blueprint("api", __name__, url_prefix="/api")
   
   
   @bp.route("/health", methods=["GET"])
   def health_check() -> Dict[str, str]:
       """Health check endpoint.
       
       Returns:
           Dict with status message.
       """
       return jsonify({"status": "healthy"})
   
   
   @bp.route("/generate", methods=["POST"])
   @api_error_handler
   def generate_manzai() -> Dict[str, Any]:
       """Generate manzai script using Ollama.
       
       Returns:
           Dict containing the generated script.
       """
       data = request.get_json()
       if not data or "topic" not in data:
           raise APIError("トピックが指定されていません", 400)
           
       topic = data["topic"]
       temperature = data.get("temperature", 0.7)
       
       # Ollamaサーバーが起動しているか確認
       ollama_url = current_app.config["OLLAMA_URL"]
       try:
           response = requests.get(f"{ollama_url}/api/tags", timeout=2)
           response.raise_for_status()
       except requests.RequestException:
           raise APIError(
               "Ollamaサーバーに接続できません。サーバーが起動しているか確認してください。",
               503
           )
       
       # プロンプトを読み込み
       try:
           prompt = load_prompt("manzai_prompt", topic=topic)
       except FileNotFoundError:
           raise APIError("プロンプトテンプレートが見つかりません", 500)
       
       # 台本を生成
       try:
           ollama_service = OllamaService()
           raw_response = ollama_service.generate_text(
               prompt=prompt,
               temperature=temperature,
               max_tokens=1500
           )
       except Exception as e:
           raise APIError(f"台本の生成中にエラーが発生しました: {str(e)}", 500)
       
       # 生成された台本を解析
       script_lines = parse_manzai_script(raw_response)
       
       return jsonify({
           "topic": topic,
           "script": script_lines
       })
   
   
   @bp.route("/synthesize", methods=["POST"])
   @api_error_handler
   def synthesize_voice() -> Dict[str, Any]:
       """Synthesize voice from text using VoiceVox.
       
       Returns:
           Dict containing audio file path and timing data.
       """
       data = request.get_json()
       if not data or "text" not in data:
           raise APIError("テキストが指定されていません", 400)
           
       text = data["text"]
       speaker_id = data.get("speaker_id", 1)  # デフォルトはずんだもん
       
       # VoiceVoxサーバーが起動しているか確認
       voicevox_url = current_app.config["VOICEVOX_URL"]
       try:
           response = requests.get(f"{voicevox_url}/version", timeout=2)
           response.raise_for_status()
       except requests.RequestException:
           raise APIError(
               "VoiceVoxサーバーに接続できません。サーバーが起動しているか確認してください。", 
               503
           )
       
       # 音声合成
       try:
           voicevox_service = VoiceVoxService()
           file_path, accent_data = voicevox_service.synthesize_voice(
               text=text,
               speaker_id=speaker_id
           )
       except Exception as e:
           raise APIError(f"音声合成中にエラーが発生しました: {str(e)}", 500)
       
       # クライアントに返すURLを構築
       filename = os.path.basename(file_path)
       audio_url = request.host_url.rstrip('/') + f"/audio/{filename}"
       
       return jsonify({
           "audio_url": audio_url,
           "timing_data": accent_data
       })
   
   
   @bp.route("/synthesize_script", methods=["POST"])
   @api_error_handler
   def synthesize_script() -> Dict[str, Any]:
       """Synthesize voice for a manzai script.
       
       Returns:
           Dict containing audio files and timing data for each line.
       """
       data = request.get_json()
       if not data or "script" not in data:
           raise APIError("台本が指定されていません", 400)
           
       script = data["script"]
       tsukkomi_id = data.get("tsukkomi_id", 1)  # ツッコミ役の声
       boke_id = data.get("boke_id", 3)         # ボケ役の声
       
       # VoiceVoxサーバーが起動しているか確認
       voicevox_url = current_app.config["VOICEVOX_URL"]
       try:
           response = requests.get(f"{voicevox_url}/version", timeout=2)
           response.raise_for_status()
       except requests.RequestException:
           raise APIError(
               "VoiceVoxサーバーに接続できません。サーバーが起動しているか確認してください。", 
               503
           )
       
       # 台本の各行に対して音声合成
       try:
           voicevox_service = VoiceVoxService()
           results = []
           
           for line in script:
               speaker = line.get("speaker", "tsukkomi")
               text = line.get("text", "")
               
               if not text:
                   continue
                   
               # 話者IDを選択
               speaker_id = tsukkomi_id if speaker == "tsukkomi" else boke_id
               
               # 音声合成
               file_path, accent_data = voicevox_service.synthesize_voice(
                   text=text,
                   speaker_id=speaker_id
               )
               
               # URL構築
               filename = os.path.basename(file_path)
               audio_url = request.host_url.rstrip('/') + f"/audio/{filename}"
               
               results.append({
                   "speaker": speaker,
                   "text": text,
                   "audio_url": audio_url,
                   "timing_data": accent_data
               })
       except Exception as e:
           raise APIError(f"音声合成中にエラーが発生しました: {str(e)}", 500)
       
       return jsonify({
           "results": results
       })
   
   
   @bp.route("/speakers", methods=["GET"])
   @api_error_handler
   def get_speakers() -> Dict[str, Any]:
       """Get list of available VoiceVox speakers.
       
       Returns:
           Dict containing list of speakers.
       """
       # VoiceVoxサーバーが起動しているか確認
       voicevox_url = current_app.config["VOICEVOX_URL"]
       try:
           response = requests.get(f"{voicevox_url}/version", timeout=2)
           response.raise_for_status()
       except requests.RequestException:
           raise APIError(
               "VoiceVoxサーバーに接続できません。サーバーが起動しているか確認してください。", 
               503
           )
       
       # 話者一覧を取得
       try:
           voicevox_service = VoiceVoxService()
           speakers = voicevox_service.get_speakers()
       except Exception as e:
           raise APIError(f"話者一覧の取得中にエラーが発生しました: {str(e)}", 500)
       
       # 簡略化したリストを返す
       simplified = []
       for speaker_info in speakers:
           for style in speaker_info.get("styles", []):
               simplified.append({
                   "id": style.get("id"),
                   "name": f"{speaker_info.get('name')} ({style.get('name')})"
               })
               
       return jsonify({
           "speakers": simplified
       })
   
   
   def parse_manzai_script(raw_script: str) -> list[Dict[str, str]]:
       """Parse raw manzai script into structured format.
       
       Args:
           raw_script: Raw script from Ollama.
           
       Returns:
           List of dialogue lines with speaker and text.
       """
       import re
       
       # コードブロックから内容を抽出
       code_block_pattern = r"```(.*?)```"
       match = re.search(code_block_pattern, raw_script, re.DOTALL)
       if match:
           script_content = match.group(1)
       else:
           script_content = raw_script
           
       # 各行をパース
       result = []
       pattern = r"([AB]):\s+(.*)"
       
       for line in script_content.splitlines():
           match = re.match(pattern, line.strip())
           if match:
               speaker, text = match.groups()
               result.append({
                   "speaker": "tsukkomi" if speaker == "A" else "boke",
                   "text": text
               })
               
       # 結果が空の場合はエラー
       if not result:
           raise APIError("生成された台本が正しい形式ではありません", 422)
               
       return result
   EOF
   ```

3. **エラーハンドリングをFlaskアプリに統合**
   ```bash
   # Flaskアプリにエラーハンドリングを統合
   cat > src/backend/app/__init__.py << 'EOF'
   """Flask application factory."""
   from flask import Flask, send_from_directory
   from flask_cors import CORS
   import os
   import logging

   from backend.app.config import Config, DevelopmentConfig
   from backend.app.utils.error_handlers import APIError, handle_api_error
   
   def create_app(config_object: Config = DevelopmentConfig) -> Flask:
       """Create and configure the Flask application.
   
       Args:
           config_object: Configuration object to use.
   
       Returns:
           Configured Flask application.
       """
       app = Flask(__name__)
       app.config.from_object(config_object)
       CORS(app)
       
       # ロギングの設定
       if not app.debug:
           logging.basicConfig(
               level=logging.INFO,
               format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
           )
       
       # エラーハンドラを登録
       app.register_error_handler(APIError, handle_api_error)
   
       # Register blueprints
       from backend.app.routes import api
       app.register_blueprint(api.bp)
       
       # Static files route
       @app.route('/audio/<path:filename>')
       def serve_audio(filename):
           return send_from_directory(
               os.path.join(app.root_path, 'static/audio'), 
               filename
           )
   
       return app
   EOF
   ```

この開発ステップでは、キャラクター切り替え機能とエラーハンドリングの強化に焦点を当てました。キャラクターの管理システムを導入し、ユーザーがキャラクターのモデルと音声を選択できるようになりました。また、バックエンドとフロントエンドの両方でエラーハンドリングを改善し、ユーザーに分かりやすいエラーメッセージを表示できるようになりました。次のステップでは、モデル管理とカスタマイズ機能を強化します。