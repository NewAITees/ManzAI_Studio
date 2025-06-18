import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * 音声再生コンポーネント
 * @param {Object} props - コンポーネントのプロパティ
 * @param {Array} props.audioData - 音声データの配列
 * @param {Function} props.onPlayStateChange - 再生状態が変わったときのコールバック関数
 */
const AudioPlayer = ({ audioData, onPlayStateChange }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(-1);
  const audioRefs = useRef([]);
  const currentAudioRef = useRef(null);

  // 音声データが変わったら、参照を初期化
  useEffect(() => {
    audioRefs.current = audioData.map(() => null);
    setCurrentIndex(-1);
    setIsPlaying(false);
    onPlayStateChange(false, null, -1);
  }, [audioData, onPlayStateChange]);

  // 個別の音声ファイルの再生
  const playAudio = async (index) => {
    if (index >= audioData.length) {
      // すべての音声再生が終了
      setIsPlaying(false);
      setCurrentIndex(-1);
      onPlayStateChange(false, null, -1);
      return;
    }

    try {
      const audio = audioRefs.current[index];
      if (!audio) return;

      // 現在の音声と再生位置を設定
      currentAudioRef.current = audio;
      setCurrentIndex(index);

      // 再生状態をアップデート
      setIsPlaying(true);
      onPlayStateChange(true, audio, index);

      // 音声の再生
      audio.currentTime = 0;
      await audio.play();

      // この音声の再生が終わったら次の音声を再生
      audio.onended = () => {
        playAudio(index + 1);
      };
    } catch (error) {
      console.error('Error playing audio:', error);
      setIsPlaying(false);
      setCurrentIndex(-1);
      onPlayStateChange(false, null, -1);
    }
  };

  // 再生ボタンのクリックハンドラ
  const handlePlay = async () => {
    if (isPlaying) {
      // 再生中なら停止
      handleStop();
    } else {
      // 停止中なら再生
      playAudio(0);
    }
  };

  // 停止ボタンのクリックハンドラ
  const handleStop = () => {
    // すべての音声を停止
    audioRefs.current.forEach(audio => {
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
      }
    });

    setIsPlaying(false);
    setCurrentIndex(-1);
    onPlayStateChange(false, null, -1);
  };

  return (
    <div className="audio-player">
      {/* 音声ファイル要素の生成 (非表示) */}
      {audioData.map((audio, index) => (
        <audio
          key={index}
          ref={el => audioRefs.current[index] = el}
          src={audio.audio_path}
          preload="auto"
          data-testid={`audio-element-${index}`}
        />
      ))}

      {/* 再生/停止ボタン */}
      <button
        onClick={handlePlay}
        disabled={audioData.length === 0}
        data-testid="play-button"
      >
        {isPlaying ? '停止' : '再生'}
      </button>

      {/* 再生中の音声表示 */}
      {isPlaying && currentIndex >= 0 && (
        <div className="now-playing">
          再生中: {audioData[currentIndex]?.role === 'tsukkomi' ? 'ツッコミ' : 'ボケ'}
        </div>
      )}
    </div>
  );
};

AudioPlayer.propTypes = {
  audioData: PropTypes.arrayOf(
    PropTypes.shape({
      role: PropTypes.oneOf(['tsukkomi', 'boke']).isRequired,
      audio_path: PropTypes.string.isRequired
    })
  ).isRequired,
  onPlayStateChange: PropTypes.func.isRequired
};

export default AudioPlayer;
