import React, { useState, useEffect, useRef } from 'react';
import InputForm from './components/InputForm';
import DisplayWindow from './components/DisplayWindow';
import AudioPlayer from './components/AudioPlayer';
import { calculateMouthOpenness } from './utils/lipSync';
import { generateManzaiScript, getTimingData } from './services/api';
import './App.css';

/**
 * ManzAI Studioのメインアプリケーションコンポーネント
 */
const App = () => {
  // 状態管理
  const [isGenerating, setIsGenerating] = useState(false);
  const [script, setScript] = useState(null);
  const [audioData, setAudioData] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentAudioIndex, setCurrentAudioIndex] = useState(-1);
  const [mouthOpenValue, setMouthOpenValue] = useState(0);
  const [timingData, setTimingData] = useState(null);
  
  // アニメーションと音声の同期用
  const requestRef = useRef(null);
  const startTimeRef = useRef(0);
  const audioElementRef = useRef(null);
  
  // タイミングデータを使って口の動きを更新するアニメーションフレーム
  const animate = () => {
    if (isPlaying && timingData && audioElementRef.current) {
      const currentTime = audioElementRef.current.currentTime * 1000; // 秒からミリ秒に変換
      const openness = calculateMouthOpenness(timingData, currentTime);
      setMouthOpenValue(openness);
    }
    
    requestRef.current = requestAnimationFrame(animate);
  };
  
  // 再生状態が変わったときの処理
  useEffect(() => {
    if (isPlaying) {
      requestRef.current = requestAnimationFrame(animate);
      startTimeRef.current = performance.now();
    } else {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
      setMouthOpenValue(0);
    }
    
    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, [isPlaying, timingData]);

  // 現在の音声が変わったときにタイミングデータを取得
  useEffect(() => {
    if (currentAudioIndex >= 0 && script && script[currentAudioIndex]) {
      const fetchTimingData = async () => {
        try {
          const text = script[currentAudioIndex].text;
          const speakerId = script[currentAudioIndex].role === 'tsukkomi' ? 1 : 2;
          const data = await getTimingData(text, speakerId);
          setTimingData(data);
        } catch (error) {
          console.error('Failed to fetch timing data:', error);
        }
      };
      
      fetchTimingData();
    }
  }, [currentAudioIndex, script]);
  
  // スクリプト生成リクエストの処理
  const handleGenerateScript = async (topic) => {
    setIsGenerating(true);
    
    try {
      // APIサービスを使用して漫才スクリプトを生成
      // 明示的にモックデータを使用しないように設定
      const data = await generateManzaiScript(topic, false);
      
      // 結果を状態に設定
      setScript(data.script);
      setAudioData(data.audio_data || []);
      
    } catch (error) {
      console.error('Error generating script:', error);
      alert(`スクリプト生成中にエラーが発生しました: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };
  
  // 音声再生状態の変更ハンドラ
  const handlePlayStateChange = (playing, audioElement = null, index = -1) => {
    setIsPlaying(playing);
    setCurrentAudioIndex(index);
    audioElementRef.current = audioElement;
  };
  
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>ManzAI Studio</h1>
      </header>
      
      <main className="app-main">
        <section className="input-section">
          <InputForm
            onSubmit={handleGenerateScript}
            isGenerating={isGenerating}
          />
        </section>
        
        {script && (
          <>
            <section className="display-section">
              <div className="characters-container">
                {/* ツッコミ役のLive2D表示 */}
                <div className="character tsukkomi">
                  <DisplayWindow
                    isDisplayMode={true}
                    modelPath="/live2d/models/tsukkomi/model.json"
                    isPlaying={isPlaying && audioData[currentAudioIndex]?.role === 'tsukkomi'}
                    mouthOpenValue={
                      isPlaying && audioData[currentAudioIndex]?.role === 'tsukkomi'
                        ? mouthOpenValue
                        : 0
                    }
                  />
                </div>
                
                {/* ボケ役のLive2D表示 */}
                <div className="character boke">
                  <DisplayWindow
                    isDisplayMode={true}
                    modelPath="/live2d/models/boke/model.json"
                    isPlaying={isPlaying && audioData[currentAudioIndex]?.role === 'boke'}
                    mouthOpenValue={
                      isPlaying && audioData[currentAudioIndex]?.role === 'boke'
                        ? mouthOpenValue
                        : 0
                    }
                  />
                </div>
              </div>
            </section>
            
            <section className="script-section">
              <div className="script-container">
                <h2>漫才スクリプト</h2>
                <div className="script-lines">
                  {script.map((line, index) => (
                    <div
                      key={index}
                      className={`script-line ${line.role} ${index === currentAudioIndex ? 'current' : ''}`}
                    >
                      <strong>{line.role === 'tsukkomi' ? 'ツッコミ' : 'ボケ'}:</strong> {line.text}
                    </div>
                  ))}
                </div>
              </div>
            </section>
            
            <section className="player-section">
              <AudioPlayer
                audioData={audioData}
                onPlayStateChange={handlePlayStateChange}
              />
            </section>
          </>
        )}
      </main>
      
      <footer className="app-footer">
        <p>© 2023 ManzAI Studio - ローカルで動作する漫才生成・実演Webアプリケーション</p>
      </footer>
    </div>
  );
};

export default App; 