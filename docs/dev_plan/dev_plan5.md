# ManzAI Studio 開発工程書

## 開発ステップ5: Live2D SDKの実装と音声同期機能の高度化

### 実際のLive2D SDKの導入

1. **Live2D Cubism SDKのダウンロードと設定**
   ```bash
   # Live2D Cubism SDK for Webのダウンロードとセットアップ
   mkdir -p frontend/public/live2d_sdk
   cd frontend/public/live2d_sdk
   
   # 注: 実際にはLive2D公式サイトからSDKをダウンロードして配置する必要があります
   # 以下はダウンロード後のファイル配置を想定した構造
   mkdir -p Core Samples Framework
   
   # SDKをダウンロードして展開後、必要なファイルをコピー
   # cp -r /path/to/downloaded/sdk/Core/* Core/
   # cp -r /path/to/downloaded/sdk/Framework/* Framework/
   
   cd ../../..
   ```

2. **Live2D SDKをHTMLに組み込む**
   ```bash
   # HTMLにLive2D SDKのスクリプトを追加
   cat > frontend/public/index.html << 'EOF'
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
       
       <!-- Live2D SDK Core Library -->
       <script src="%PUBLIC_URL%/live2d_sdk/Core/live2dcubismcore.js"></script>
       
       <!-- Live2D SDK Framework -->
       <script src="%PUBLIC_URL%/live2d_sdk/Framework/effect/cubismbreath.js"></script>
       <script src="%PUBLIC_URL%/live2d_sdk/Framework/effect/cubismeyeblink.js"></script>
       <script src="%PUBLIC_URL%/live2d_sdk/Framework/live2dcubismframework.js"></script>
       <script src="%PUBLIC_URL%/live2d_sdk/Framework/math/cubismmatrix44.js"></script>
       <script src="%PUBLIC_URL%/live2d_sdk/Framework/model/cubismmoc.js"></script>
       <script src="%PUBLIC_URL%/live2d_sdk/Framework/model/cubismmodel.js"></script>
       <script src="%PUBLIC_URL%/live2d_sdk/Framework/motion/cubismmotion.js"></script>
       <script src="%PUBLIC_URL%/live2d_sdk/Framework/physics/cubismphysics.js"></script>
       <script src="%PUBLIC_URL%/live2d_sdk/Framework/rendering/cubismrenderer.js"></script>
       <script src="%PUBLIC_URL%/live2d_sdk/Framework/rendering/cubismrenderer_webgl.js"></script>
       <script src="%PUBLIC_URL%/live2d_sdk/Framework/utils/cubismdebug.js"></script>
     </head>
     <body>
       <noscript>You need to enable JavaScript to run this app.</noscript>
       <div id="root"></div>
     </body>
   </html>
   EOF
   ```

### Live2D実装の完成

1. **Live2D初期化ユーティリティの完成**
   ```bash
   # Live2D初期化ユーティリティを実装
   cat > frontend/src/utils/live2dInitializer.js << 'EOF'
   /**
    * Live2D初期化ユーティリティ
    */
   
   // Live2Dモデルローダー
   export class Live2DModelLoader {
     constructor(canvasId) {
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
         
         // モデル行列の設定
         this.modelMatrix = new window.Live2DCubismFramework.CubismMatrix44();
         this.modelMatrix.scale(1.0, 1.0);
         this.modelMatrix.translateX(0);
         this.modelMatrix.translateY(0);
         
         // アニメーションの初期化
         // このアプリケーションでは主にリップシンクを制御するので、
         // 他のアニメーションは簡易的に実装
         
         // 描画ループの開始
         this.startRenderLoop();
         
         return true;
       } catch (error) {
         console.error('Failed to load Live2D model:', error);
         return false;
       }
     }
     
     async createTexture(texturePath) {
       return new Promise((resolve, reject) => {
         const img = new Image();
         img.onload = () => {
           const texture = this.gl.createTexture();
           this.gl.bindTexture(this.gl.TEXTURE_2D, texture);
           this.gl.texImage2D(this.gl.TEXTURE_2D, 0, this.gl.RGBA, this.gl.RGBA, this.gl.UNSIGNED_BYTE, img);
           this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_MAG_FILTER, this.gl.LINEAR);
           this.gl.texParameteri(this.gl.TEXTURE_2D, this.gl.TEXTURE_MIN_FILTER, this.gl.LINEAR_MIPMAP_LINEAR);
           this.gl.generateMipmap(this.gl.TEXTURE_2D);
           this.gl.bindTexture(this.gl.TEXTURE_2D, null);
           resolve(texture);
         };
         img.onerror = reject;
         img.src = texturePath;
       });
     }
     
     startRenderLoop() {
       const loop = () => {
         if (this.isLostContext) return;
         
         // フレームカウントの更新
         this.frameCount++;
         
         // デルタタイムの計算
         const time = Date.now() - this.startTime;
         const deltaTime = (time - this.previousTime) / 1000;
         this.previousTime = time;
         
         // キャンバスサイズの更新
         this.updateCanvasSize();
         
         // 描画処理
         this.draw(deltaTime);
         
         // 次のフレームをリクエスト
         this.rafId = requestAnimationFrame(loop);
       };
       
       this.previousTime = Date.now() - this.startTime;
       loop();
     }
     
     updateCanvasSize() {
       // キャンバスサイズを更新
       const width = this.canvas.clientWidth;
       const height = this.canvas.clientHeight;
       
       if (this.canvas.width !== width || this.canvas.height !== height) {
         this.canvas.width = width;
         this.canvas.height = height;
         this.gl.viewport(0, 0, width, height);
       }
     }
     
     draw(deltaTime) {
       // モデルが読み込まれていなければ何もしない
       if (!this.model || !this.renderer) return;
       
       // WebGLの設定
       this.gl.clearColor(0.0, 0.0, 0.0, 0.0);
       this.gl.enable(this.gl.BLEND);
       this.gl.blendFunc(this.gl.SRC_ALPHA, this.gl.ONE_MINUS_SRC_ALPHA);
       this.gl.clear(this.gl.COLOR_BUFFER_BIT);
       
       // モデルの更新
       this.model.update();
       
       // レンダリング
       this.renderer.setRenderState(this.gl, 0, 0, this.canvas.width, this.canvas.height);
       this.renderer.setMvpMatrix(this.modelMatrix);
       this.renderer.drawModel();
     }
     
     // パラメータの設定
     setParameter(parameterName, value) {
       if (!this.model) return;
       
       // パラメータIDを取得
       const parameterId = window.Live2DCubismFramework.CubismFramework.getIdManager().getId(parameterName);
       
       // パラメータの値を設定
       this.model.setParameterValue(parameterId, value);
     }
     
     // パラメータの取得
     getParameter(parameterName) {
       if (!this.model) return 0;
       
       // パラメータIDを取得
       const parameterId = window.Live2DCubismFramework.CubismFramework.getIdManager().getId(parameterName);
       
       // パラメータの値を取得
       return this.model.getParameterValue(parameterId);
     }
     
     // コンテキスト消失時の処理
     handleContextLost(event) {
       event.preventDefault();
       this.isLostContext = true;
       
       if (this.rafId !== null) {
         cancelAnimationFrame(this.rafId);
         this.rafId = null;
       }
     }
     
     // コンテキスト復元時の処理
     handleContextRestored(event) {
       this.isLostContext = false;
       this.gl = this.canvas.getContext('webgl');
       
       // モデルの再読み込み
       // 注: このアプリケーションでは実装を簡略化しています
     }
     
     // リソースの解放
     release() {
       if (this.rafId !== null) {
         cancelAnimationFrame(this.rafId);
         this.rafId = null;
       }
       
       if (this.model) {
         this.model.release();
         this.model = null;
       }
       
       if (this.renderer) {
         this.renderer.release();
         this.renderer = null;
       }
     }
   }
   
   // Live2Dモデルの口の動きを制御するクラス
   export class LipSyncController {
     constructor(modelLoader) {
       this.modelLoader = modelLoader;
       this.isActive = false;
       this.currentMouthOpenValue = 0;
       this.targetMouthOpenValue = 0;
       this.mouthOpenSpeed = 0.1; // 口の開閉速度
     }
     
     // リップシンクの更新
     update() {
       if (!this.isActive) return;
       
       // 口の開閉値を目標値に近づける
       if (this.currentMouthOpenValue < this.targetMouthOpenValue) {
         this.currentMouthOpenValue = Math.min(this.currentMouthOpenValue + this.mouthOpenSpeed, this.targetMouthOpenValue);
       } else if (this.currentMouthOpenValue > this.targetMouthOpenValue) {
         this.currentMouthOpenValue = Math.max(this.currentMouthOpenValue - this.mouthOpenSpeed, this.targetMouthOpenValue);
       }
       
       // モデルのパラメータを更新
       this.modelLoader.setParameter('ParamMouthOpenY', this.currentMouthOpenValue);
     }
     
     // 口の開閉値を設定
     setMouthOpen(value) {
       this.targetMouthOpenValue = value;
     }
     
     // リップシンクの開始
     start() {
       this.isActive = true;
     }
     
     // リップシンクの停止
     stop() {
       this.isActive = false;
       this.targetMouthOpenValue = 0;
     }
   }
   
   // モデルとコントローラのインスタンスを作成して公開
   let modelLoader = null;
   let lipSyncController = null;
   
   // Live2Dモデルを初期化する関数
   export const initializeLive2D = async (canvasId, modelPath) => {
     try {
       modelLoader = new Live2DModelLoader(canvasId);
       const success = await modelLoader.loadModel(modelPath);
       
       if (success) {
         lipSyncController = new LipSyncController(modelLoader);
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
   
   // 口の開閉を制御する関数
   export const updateMouth = (live2dInstance, value) => {
     if (!live2dInstance || !live2dInstance.lipSyncController) return;
     
     live2dInstance.lipSyncController.setMouthOpen(value);
     live2dInstance.lipSyncController.update();
   };
   
   // リソースを解放する関数
   export const releaseLive2D = (live2dInstance) => {
     if (!live2dInstance || !live2dInstance.modelLoader) return;
     
     live2dInstance.modelLoader.release();
   };
   EOF
   ```

2. **Live2Dステージコンポーネントの改良**
   ```bash
   # Live2Dステージコンポーネントを更新
   cat > frontend/src/components/Live2DStage.js << 'EOF'
   import React, { useEffect, useRef, useState, useCallback } from 'react';
   import { initializeLive2D, updateMouth, releaseLive2D } from '../utils/live2dInitializer';
   
   const Live2DStage = ({ script, audioData }) => {
     const canvasRef = useRef(null);
     const [live2dInstance, setLive2dInstance] = useState(null);
     const [isPlaying, setIsPlaying] = useState(false);
     const [currentLine, setCurrentLine] = useState(-1);
     const audioRef = useRef(null);
     const animationFrameRef = useRef(null);
     const lipSyncIntervalRef = useRef(null);
     
     // Live2Dモデルの初期化
     useEffect(() => {
       const initModel = async () => {
         try {
           // 注: 実際のモデルパスを指定
           const modelPath = '/live2d/models/character1/model.json';
           const instance = await initializeLive2D('live2d-canvas', modelPath);
           
           if (instance) {
             console.log('Live2D model initialized successfully');
             setLive2dInstance(instance);
             
             // リップシンクを開始
             instance.lipSyncController.start();
           } else {
             console.error('Failed to initialize Live2D model');
           }
         } catch (error) {
           console.error('Error initializing Live2D:', error);
         }
       };
       
       initModel();
       
       // クリーンアップ
       return () => {
         if (animationFrameRef.current) {
           cancelAnimationFrame(animationFrameRef.current);
         }
         
         if (lipSyncIntervalRef.current) {
           clearInterval(lipSyncIntervalRef.current);
         }
         
         if (live2dInstance) {
           releaseLive2D(live2dInstance);
         }
       };
     }, []);
     
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
     const startLipSync = useCallback((audio, timingData) => {
       if (!live2dInstance) return;
       
       const animate = () => {
         if (!audio || audio.paused || audio.ended) {
           updateMouth(live2dInstance, 0);
           cancelAnimationFrame(animationFrameRef.current);
           return;
         }
         
         const currentTime = audio.currentTime * 1000; // ミリ秒に変換
         const mouthOpenValue = calculateMouthOpenValue(currentTime, timingData);
         
         updateMouth(live2dInstance, mouthOpenValue);
         
         animationFrameRef.current = requestAnimationFrame(animate);
       };
       
       // アニメーションの開始
       animationFrameRef.current = requestAnimationFrame(animate);
     }, [live2dInstance, calculateMouthOpenValue]);
     
     // 音声再生とリップシンク
     useEffect(() => {
       if (!audioData || audioData.length === 0 || !live2dInstance) return;
       
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
           updateMouth(live2dInstance, 0);
           return;
         }
         
         setCurrentLine(index);
         const lineData = audioData[index];
         const audio = new Audio(lineData.audio_url);
         audioRef.current = audio;
         
         // 音声再生開始時の処理
         audio.onplay = () => {
           startLipSync(audio, lineData.timing_data);
         };
         
         // 音声再生終了時の処理
         audio.onended = () => {
           updateMouth(live2dInstance, 0);
           
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
         
         const container = canvasRef.current.parentElement;
         const existingButton = container.querySelector('.play-button');
         if (existingButton) {
           container.removeChild(existingButton);
         }
         container.appendChild(playButton);
       }
       
     }, [audioData, live2dInstance, isPlaying, startLipSync]);
     
     return (
       <div className="live2d-container" style={{ position: 'relative', width: '100%', height: '100%' }}>
         <canvas
           id="live2d-canvas"
           ref={canvasRef}
           width="512"
           height="512"
           style={{ width: '100%', height: '100%', background: 'transparent' }}
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

### UI改良とユーザー体験の向上

1. **UIスタイルの改良**
   ```bash
   # 改良されたスタイルを適用
   cat > frontend/src/App.css << 'EOF'
   .App {
     text-align: center;
     display: flex;
     flex-direction: column;
     min-height: 100vh;
   }
   
   .App-header {
     background-color: #2c3e50;
     padding: 20px;
     color: white;
     box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
   }
   
   .App-header h1 {
     margin: 0;
     font-size: 2.5rem;
   }
   
   .App-header p {
     margin: 10px 0 0;
     font-size: 1.1rem;
     opacity: 0.8;
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
     border-radius: 10px;
     box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
     overflow: hidden;
     background: linear-gradient(to bottom, #e6f7ff, #f2f2f2);
     margin-bottom: 20px;
   }
   
   .control-container {
     flex: 1;
     padding: 0 20px;
   }
   
   .App-footer {
     background-color: #2c3e50;
     color: white;
     padding: 15px;
     margin-top: auto;
   }
   
   /* ManzaiGenerator スタイル */
   .manzai-generator {
     max-width: 500px;
     margin: 0 auto;
     background: white;
     padding: 20px;
     border-radius: 10px;
     box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
   }
   
   .manzai-generator h2 {
     color: #2c3e50;
     margin-top: 0;
     border-bottom: 2px solid #3498db;
     padding-bottom: 10px;
   }
   
   .form-group {
     margin-bottom: 20px;
   }
   
   .form-group label {
     display: block;
     margin-bottom: 5px;
     font-weight: bold;
     color: #333;
     text-align: left;
   }
   
   .form-control {
     width: 100%;
     padding: 10px;
     border: 1px solid #ddd;
     border-radius: 5px;
     font-size: 16px;
   }
   
   .submit-button {
     background-color: #3498db;
     color: white;
     border: none;
     padding: 12px 20px;
     font-size: 16px;
     border-radius: 5px;
     cursor: pointer;
     width: 100%;
     margin-top: 10px;
     transition: background-color 0.3s;
   }
   
   .submit-button:hover {
     background-color: #2980b9;
   }
   
   .submit-button:disabled {
     background-color: #95a5a6;
     cursor: not-allowed;
   }
   
   .error-message {
     color: #e74c3c;
     background-color: #fadbd8;
     padding: 10px;
     border-radius: 5px;
     margin-top: 15px;
     text-align: left;
   }
   
   .instructions {
     margin-top: 30px;
     text-align: left;
     background-color: #f9f9f9;
     padding: 15px;
     border-radius: 5px;
   }
   
   .instructions h3 {
     color: #2c3e50;
     margin-top: 0;
   }
   
   .instructions ol {
     padding-left: 20px;
   }
   
   .instructions li {
     margin-bottom: 10px;
   }
   
   /* 再生ボタンスタイル */
   .play-button {
     padding: 12px 25px;
     font-size: 16px;
     background-color: #2ecc71;
     color: white;
     border: none;
     border-radius: 5px;
     cursor: pointer;
     transition: background-color 0.3s;
   }
   
   .play-button:hover {
     background-color: #27ae60;
   }
   
   /* 台詞表示スタイル */
   .dialogue-display {
     background-color: rgba(0, 0, 0, 0.7);
     color: white;
     padding: 15px;
     border-radius: 10px;
     max-width: 80%;
     margin: 0 auto;
     position: absolute;
     bottom: 30px;
     left: 10%;
     right: 10%;
     font-size: 18px;
     z-index: 10;
     box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
   }
   EOF
   ```

2. **ローディングインジケーターの追加**
   ```bash
   # ローディングコンポーネントの作成
   mkdir -p frontend/src/components/ui
   cat > frontend/src/components/ui/LoadingSpinner.js << 'EOF'
   import React from 'react';
   
   const LoadingSpinner = ({ text = 'Loading...' }) => {
     return (
       <div style={{
         display: 'flex',
         flexDirection: 'column',
         alignItems: 'center',
         justifyContent: 'center',
         padding: '20px'
       }}>
         <div style={{
           border: '4px solid rgba(0, 0, 0, 0.1)',
           borderLeft: '4px solid #3498db',
           borderRadius: '50%',
           width: '40px',
           height: '40px',
           animation: 'spin 1s linear infinite',
           marginBottom: '10px'
         }} />
         <style jsx>{`
           @keyframes spin {
             0% { transform: rotate(0deg); }
             100% { transform: rotate(360deg); }
           }
         `}</style>
         <p style={{ color: '#333', fontSize: '16px' }}>{text}</p>
       </div>
     );
   };
   
   export default LoadingSpinner;
   EOF
   ```

3. **漫才生成フォームコンポーネントの改良**
   ```bash
   # ManzaiGeneratorコンポーネントを更新
   cat > frontend/src/components/ManzaiGenerator.js << 'EOF'
   import React, { useState, useEffect } from 'react';
   import { generateManzai, synthesizeScript, getSpeakers } from '../services/api';
   import LoadingSpinner from './ui/LoadingSpinner';
   
   const ManzaiGenerator = ({ onScriptGenerated, isLoading, setIsLoading, error, setError }) => {
     const [topic, setTopic] = useState('');
     const [speakers, setSpeakers] = useState([]);
     const [tsukkomiId, setTsukkomiId] = useState(1); // デフォルト値
     const [bokeId, setBokeId] = useState(3); // デフォルト値
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
         const audioData = await synthesizeScript(script, tsukkomiId, bokeId);
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
         setError('漫才の生成中にエラーが発生しました。サーバーの状態を確認してください。');
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
                 漫才を生成
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

### サンプルLive2Dモデルの準備

1. **サンプルモデルディレクトリの作成**
   ```bash
   mkdir -p frontend/public/live2d/models/character1
   mkdir -p frontend/public/live2d/models/character2
   
   # サンプルモデル情報の追加
   cat > frontend/public/live2d/models/README.md << 'EOF'
   # Live2Dモデルについて
   
   このディレクトリには、漫才の実演に使用するLive2Dモデルを配置します。
   
   ## モデルの設置方法
   
   1. Live2D Cubism Viewerなどで作成/エクスポートしたLive2Dモデル(.model3.json)をcharacter1およびcharacter2フォルダ内に配置します
   2. model.jsonファイルを以下のような内容で作成します（実際のファイル名に合わせて変更してください）
   
   ```json
   {
     "version": "Sample 1.0.0",
     "model": "your_model_name.model3.json",
     "textures": [
       "your_texture_name.png"
     ],
     "motions": {
       "idle": [
         {
           "file": "your_motion_name.motion3.json"
         }
       ]
     }
   }
   ```
   
   ## 無料/商用利用可能なLive2Dモデル
   
   開発やテスト用に、以下のようなサイトから無料で利用可能なLive2Dモデルを入手できます：
   
   - Live2D公式サンプルモデル
   - VRoid Hubで公開されているLive2D対応モデル（利用規約を確認）
   - 各種フリーLive2Dモデル配布サイト
   
   利用にあたっては、各モデルのライセンスや利用規約を必ず確認してください。
   EOF
   ```

2. **モデル情報の設定ファイル**
   ```bash
   # 設定ファイルの作成
   cat > frontend/src/config.js << 'EOF'
   /**
    * アプリケーション設定
    */
   
   // Live2Dモデルの設定
   export const LIVE2D_MODELS = {
     // ツッコミ役のモデル
     TSUKKOMI: {
       path: '/live2d/models/character1/model.json',
       name: 'ツッコミ役キャラクター'
     },
     // ボケ役のモデル
     BOKE: {
       path: '/live2d/models/character2/model.json',
       name: 'ボケ役キャラクター'
     }
   };
   
   // VoiceVoxスピーカーのデフォルト設定
   export const DEFAULT_SPEAKERS = {
     TSUKKOMI_ID: 1, // デフォルトのツッコミ役の話者ID
     BOKE_ID: 3      // デフォルトのボケ役の話者ID
   };
   
   // 漫才生成の設定
   export const MANZAI_GENERATION = {
     DEFAULT_TEMPERATURE: 0.7, // 生成時のランダム性
     MAX_TOKENS: 1500         // 最大トークン数
   };
   EOF
   ```

### スクリプト実行とコマンドの改良

1. **NPMスクリプトの改良**
   ```bash
   # package.jsonにスクリプト追加
   cat > frontend/package.json << 'EOF'
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
       "eject": "react-scripts eject",
       "lint": "eslint src --ext .js,.jsx",
       "format": "prettier --write \"src/**/*.{js,jsx,css}\""
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
     "proxy": "http://localhost:5000",
     "devDependencies": {
       "eslint": "^8.38.0",
       "eslint-config-prettier": "^8.8.0",
       "eslint-plugin-prettier": "^4.2.1",
       "eslint-plugin-react": "^7.32.2",
       "prettier": "^2.8.7"
     }
   }
   EOF
   ```

2. **開発サーバー起動スクリプトの改良**
   ```bash
   cat > start_dev.sh << 'EOF'
   #!/bin/bash
   
   # 色の定義
   GREEN='\033[0;32m'
   BLUE='\033[0;34m'
   RED='\033[0;31m'
   NC='\033[0m' # No Color
   
   # 前提条件のチェック
   echo -e "${BLUE}前提条件をチェックしています...${NC}"
   
   # Ollamaが起動しているか確認
   if ! curl -s http://localhost:11434/api/tags > /dev/null; then
     echo -e "${RED}Ollamaが起動していません。モデル生成のためにOllamaを起動してください。${NC}"
     echo -e "起動コマンド: ${GREEN}ollama serve${NC}"
     exit 1
   fi
   
   # VoiceVoxが起動しているか確認
   if ! curl -s http://localhost:50021/version > /dev/null; then
     echo -e "${RED}VoiceVoxが起動していません。音声合成のためにVoiceVoxを起動してください。${NC}"
     echo -e "VoiceVoxアプリケーションを開くか、Docker Composeを使用している場合は以下のコマンドを実行してください:"
     echo -e "${GREEN}docker-compose up -d voicevox${NC}"
     exit 1
   fi
   
   # 必要なモデルがOllamaにあるか確認
   OLLAMA_MODEL=$(grep "OLLAMA_MODEL" src/backend/app/config.py | awk -F'"' '{print $2}')
   if ! curl -s http://localhost:11434/api/tags | grep -q "$OLLAMA_MODEL"; then
     echo -e "${RED}Ollamaに必要なモデル '$OLLAMA_MODEL' がインストールされていません。${NC}"
     echo -e "インストールコマンド: ${GREEN}ollama pull $OLLAMA_MODEL${NC}"
     exit 1
   fi
   
   echo -e "${GREEN}前提条件のチェックが完了しました。開発サーバーを起動します...${NC}"
   
   # バックエンドの起動
   echo -e "${BLUE}バックエンドサーバーを起動しています...${NC}"
   poetry run python -m flask --app backend/app/__init__.py run --debug &
   BACKEND_PID=$!
   
   # バックエンドが起動するまで待機
   echo -e "${BLUE}バックエンドサーバーが準備完了するまで待機しています...${NC}"
   until curl -s http://localhost:5000/api/health > /dev/null; do
     echo -n "."
     sleep 1
   done
   echo -e "${GREEN}バックエンドサーバーが起動しました！${NC}"
   
   # フロントエンドの起動
   echo -e "${BLUE}フロントエンド開発サーバーを起動しています...${NC}"
   cd frontend && npm start &
   FRONTEND_PID=$!
   
   # プロセスを終了するための関数
   function cleanup {
     echo -e "\n${BLUE}サーバーをシャットダウンしています...${NC}"
     kill $BACKEND_PID 2>/dev/null
     kill $FRONTEND_PID 2>/dev/null
     echo -e "${GREEN}サーバーが正常にシャットダウンされました。${NC}"
     exit 0
   }
   
   # Ctrl+Cでクリーンアップを実行
   trap cleanup INT
   
   echo -e "${GREEN}開発サーバーが起動しました！${NC}"
   echo -e "${BLUE}バックエンド: ${NC}http://localhost:5000"
   echo -e "${BLUE}フロントエンド: ${NC}http://localhost:3000"
   echo -e "${RED}終了するには Ctrl+C を押してください${NC}"
   
   # 待機
   wait
   EOF
   
   chmod +x start_dev.sh
   ```

この開発ステップでは、Live2D SDKの実装とフロントエンドの機能改良を行いました。リップシンク処理の高度化や、UIの改良によってユーザーエクスペリエンスが向上しています。また、フロントエンドの構造化によって、今後の拡張性も確保されています。次のステップでは、モデル切り替え機能やエラーハンドリングの強化を行います。