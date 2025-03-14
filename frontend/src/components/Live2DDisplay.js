import React, { useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { loadModel, setParameter } from '../utils/live2d';

const Live2DDisplay = ({ modelPath, isPlaying = false, mouthOpenValue = 0 }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    // モデルの読み込み
    if (canvasRef.current) {
      loadModel(modelPath);
    }
  }, [modelPath]);

  useEffect(() => {
    // 口の開閉パラメータの更新
    if (isPlaying) {
      setParameter("ParamMouthOpenY", mouthOpenValue);
    }
  }, [isPlaying, mouthOpenValue]);

  return (
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
  );
};

Live2DDisplay.propTypes = {
  modelPath: PropTypes.string.isRequired,
  isPlaying: PropTypes.bool,
  mouthOpenValue: PropTypes.number
};

export default Live2DDisplay; 