import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { loadModel, setParameter, releaseModel } from '../utils/live2d';

/**
 * Live2Dモデル表示コンポーネント
 * @param {Object} props - コンポーネントのプロパティ
 * @param {string} props.modelPath - モデルのパス
 * @param {boolean} props.isPlaying - 再生中かどうか
 * @param {number} props.mouthOpenValue - 口の開き具合（0-1）
 */
const Live2DDisplay = ({ modelPath, isPlaying = false, mouthOpenValue = 0 }) => {
  const canvasRef = useRef(null);
  const modelLoadedRef = useRef(false);

  // モデルの読み込み
  useEffect(() => {
    const loadLive2DModel = async () => {
      if (canvasRef.current) {
        try {
          await loadModel(modelPath, canvasRef.current);
          modelLoadedRef.current = true;
        } catch (error) {
          console.error('Failed to load Live2D model:', error);
        }
      }
    };

    loadLive2DModel();

    // クリーンアップ関数
    return () => {
      releaseModel();
      modelLoadedRef.current = false;
    };
  }, [modelPath]);

  // 口の開閉パラメータの更新
  useEffect(() => {
    if (modelLoadedRef.current) {
      setParameter("ParamMouthOpenY", mouthOpenValue);
    }
  }, [isPlaying, mouthOpenValue]);

  return (
    <div className="live2d-container">
      <canvas
        ref={canvasRef}
        data-testid="live2d-canvas"
        width="800"
        height="600"
        style={{
          width: '100%',
          height: '100%',
          backgroundColor: '#00ff00' // クロマキー用の緑色背景
        }}
      />
    </div>
  );
};

Live2DDisplay.propTypes = {
  modelPath: PropTypes.string.isRequired,
  isPlaying: PropTypes.bool,
  mouthOpenValue: PropTypes.number
};

export default Live2DDisplay;
