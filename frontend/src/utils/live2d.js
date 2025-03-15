/**
 * Live2D Cubism SDKを使用したモデル操作ユーティリティ
 */

// モデルと描画関連の変数
let live2dModel = null;
let canvas = null;
let gl = null;
let frameId = null;
let modelMatrix = null;
let startTime = null;
let parameters = {};

/**
 * Live2Dモデルを読み込む
 * @param {string} modelPath モデルのパス
 * @param {HTMLCanvasElement} canvasElement モデルを表示するcanvas要素
 * @returns {Promise<void>}
 */
export const loadModel = async (modelPath, canvasElement) => {
  if (!canvasElement) {
    console.error('Canvas element is not provided');
    return;
  }
  
  // キャンセル処理
  if (frameId) {
    cancelAnimationFrame(frameId);
    frameId = null;
  }
  
  // キャンバスとWebGLコンテキストの設定
  canvas = canvasElement;
  gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  
  if (!gl) {
    console.error('WebGL is not supported in this browser');
    return;
  }
  
  try {
    console.log(`Loading Live2D model: ${modelPath}`);
    
    // 実際のLive2D SDKを使用する場合は以下のコードを使用
    // ここでは、モックとして簡易的な実装を行います
    live2dModel = {
      id: Math.random().toString(36).substring(7),
      path: modelPath,
      parameters: {
        'ParamMouthOpenY': 0,
        'ParamEyeOpenY': 1,
        'ParamEyeSmile': 0,
        'ParamBrowUpZ': 0,
        'ParamBodyAngleX': 0,
        'ParamBodyAngleY': 0,
        'ParamBodyAngleZ': 0
      }
    };
    
    // 初期パラメータを設定
    parameters = { ...live2dModel.parameters };
    
    // モデル表示開始
    startTime = performance.now();
    startAnimation();
    
    return live2dModel;
  } catch (error) {
    console.error('Failed to load Live2D model:', error);
    return null;
  }
};

/**
 * Live2Dモデルのパラメータを設定
 * @param {string} paramId パラメータID
 * @param {number} value パラメータの値
 */
export const setParameter = (paramId, value) => {
  if (!live2dModel) {
    console.warn('Model is not loaded yet');
    return;
  }
  
  // パラメータを設定
  parameters[paramId] = value;
  
  // 実際のLive2D SDKを使用する場合は以下のようなコード
  // live2dModel.setParameterValueById(paramId, value);
  
  console.log(`Setting parameter ${paramId} to ${value}`);
};

/**
 * Live2Dモデルのパラメータを取得
 * @param {string} paramId パラメータID
 * @returns {number} パラメータの値
 */
export const getParameter = (paramId) => {
  if (!live2dModel) {
    console.warn('Model is not loaded yet');
    return 0;
  }
  
  return parameters[paramId] || 0;
};

/**
 * モデルのアニメーションを開始
 */
const startAnimation = () => {
  const animate = () => {
    if (!canvas || !gl || !live2dModel) return;
    
    // キャンバスのサイズを更新
    updateCanvasSize();
    
    // モデルの描画処理
    drawModel();
    
    // 次のフレームを予約
    frameId = requestAnimationFrame(animate);
  };
  
  // アニメーションの開始
  frameId = requestAnimationFrame(animate);
};

/**
 * キャンバスのサイズを更新
 */
const updateCanvasSize = () => {
  // キャンバスのサイズ調整（デバイスピクセル比対応）
  const devicePixelRatio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth * devicePixelRatio;
  const height = canvas.clientHeight * devicePixelRatio;
  
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
    gl.viewport(0, 0, width, height);
  }
};

/**
 * モデルを描画
 */
const drawModel = () => {
  // WebGLの描画設定
  gl.clearColor(0.0, 1.0, 0.0, 0.0); // クロマキー用の緑背景
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
  gl.clear(gl.COLOR_BUFFER_BIT);
  
  // 実際のLive2D SDKを使用する場合はここにモデル描画コードを追加
  // 以下はモックのため、実際には何も描画されません
  
  // 自動的に自然なまばたきアニメーションを追加
  const time = (performance.now() - startTime) / 1000;
  const blinkValue = Math.max(0, Math.cos(time * 1.5) * 0.5 + 0.5);
  parameters['ParamEyeOpenY'] = blinkValue;
  
  // 呼吸アニメーション
  const breathValue = Math.sin(time * 0.5) * 0.05;
  parameters['ParamBodyAngleY'] = breathValue;
  
  // Consoleにモデルの状態を出力（デバッグ用）
  // console.log('Drawing model with parameters:', parameters);
};

/**
 * リソースをクリーンアップ
 */
export const releaseModel = () => {
  if (frameId) {
    cancelAnimationFrame(frameId);
    frameId = null;
  }
  
  live2dModel = null;
  canvas = null;
  gl = null;
  startTime = null;
  parameters = {};
  
  console.log('Live2D model released');
}; 