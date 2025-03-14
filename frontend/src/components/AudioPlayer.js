import React, { useState, useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

const AudioPlayer = ({ audioData, onPlayStateChange }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRefs = useRef([]);

  useEffect(() => {
    // 音声ファイルの読み込み
    audioRefs.current.forEach(audio => {
      if (audio) {
        audio.load();
      }
    });
  }, [audioData]);

  const handlePlay = async () => {
    try {
      // すべての音声を順番に再生
      for (let i = 0; i < audioRefs.current.length; i++) {
        const audio = audioRefs.current[i];
        if (audio) {
          setIsPlaying(true);
          onPlayStateChange(true);
          await audio.play();
          // 再生が終わるまで待機
          await new Promise(resolve => {
            audio.onended = resolve;
          });
        }
      }
      // すべての再生が終わったら停止状態に
      setIsPlaying(false);
      onPlayStateChange(false);
    } catch (error) {
      console.error('Error playing audio:', error);
      setIsPlaying(false);
      onPlayStateChange(false);
    }
  };

  const handleStop = () => {
    // すべての音声を停止
    audioRefs.current.forEach(audio => {
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
      }
    });
    setIsPlaying(false);
    onPlayStateChange(false);
  };

  return (
    <div className="audio-player">
      {audioData.map((audio, index) => (
        <audio
          key={index}
          ref={el => audioRefs.current[index] = el}
          src={audio.audio_path}
          data-testid="audio-element"
        />
      ))}
      <button
        onClick={isPlaying ? handleStop : handlePlay}
        disabled={audioData.length === 0}
      >
        {isPlaying ? '停止' : '再生'}
      </button>
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