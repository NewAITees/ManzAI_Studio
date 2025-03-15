import React, { useState, useEffect } from 'react';
import { getLive2DModels } from '../../services/modelService';
import { useCharacters } from '../../stores/characterStore';

const ModelManager = () => {
  const [models, setModels] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  const { 
    characters, 
    activeCharacter, 
    changeCharacterModel, 
    switchActiveCharacter 
  } = useCharacters();
  
  // モデル一覧を取得
  useEffect(() => {
    const fetchModels = async () => {
      try {
        setIsLoading(true);
        const modelsList = await getLive2DModels();
        setModels(modelsList);
        setError('');
      } catch (err) {
        setError('モデル一覧の取得に失敗しました');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchModels();
  }, []);
  
  // キャラクターの種類によるモデルフィルタリング
  const filteredModels = models.filter(model => {
    // タイプが指定されていない場合は両方に表示
    if (!model.type || model.type === 'unknown') return true;
    
    return model.type === activeCharacter;
  });
  
  return (
    <div className="model-manager">
      <h2>キャラクターモデル設定</h2>
      
      <div className="character-tabs">
        <button
          className={`character-tab ${activeCharacter === 'tsukkomi' ? 'active' : ''}`}
          onClick={() => switchActiveCharacter('tsukkomi')}
        >
          ツッコミ役
        </button>
        <button
          className={`character-tab ${activeCharacter === 'boke' ? 'active' : ''}`}
          onClick={() => switchActiveCharacter('boke')}
        >
          ボケ役
        </button>
      </div>
      
      <div className="current-model">
        <h3>現在のモデル</h3>
        <div className="model-info">
          <div className="model-name">
            {characters[activeCharacter].name || characters[activeCharacter].id}
          </div>
          <div className="model-path">
            {characters[activeCharacter].modelPath}
          </div>
        </div>
      </div>
      
      {isLoading ? (
        <div className="loading">モデルを読み込み中...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : (
        <div className="models-grid">
          {filteredModels.length > 0 ? (
            filteredModels.map(model => (
              <div 
                key={model.id}
                className={`model-card ${characters[activeCharacter].id === model.id ? 'selected' : ''}`}
                onClick={() => changeCharacterModel(activeCharacter, model.id)}
              >
                <div className="model-image">
                  {model.thumbnail ? (
                    <img src={model.thumbnail} alt={model.name} />
                  ) : (
                    <div className="no-image">No Image</div>
                  )}
                </div>
                <div className="model-card-info">
                  <h4>{model.name}</h4>
                  <div className="model-id">{model.id}</div>
                </div>
              </div>
            ))
          ) : (
            <div className="no-models">
              利用可能なモデルがありません。モデルを追加してください。
            </div>
          )}
        </div>
      )}
      
      <div className="model-upload">
        <h3>モデルを追加</h3>
        <p>
          Live2Dモデルを追加するには、モデルファイル（.model3.json）と関連ファイルを
          <code>/frontend/public/live2d/models/[モデル名]/</code> ディレクトリに配置し、
          <code>model.json</code> ファイルを作成してください。
        </p>
        <p>
          詳細は <a href="https://github.com/yourusername/manzai-studio/blob/main/docs/model_setup.md" target="_blank" rel="noreferrer">モデル設定ガイド</a> を参照してください。
        </p>
      </div>
      
      <style jsx>{`
        .model-manager {
          margin-top: 20px;
        }
        
        .character-tabs {
          display: flex;
          margin-bottom: 20px;
          border: 1px solid #ddd;
          border-radius: 5px;
          overflow: hidden;
        }
        
        .character-tab {
          flex: 1;
          padding: 10px 15px;
          background: none;
          border: none;
          cursor: pointer;
          font-size: 16px;
          transition: background-color 0.2s;
        }
        
        .character-tab.active {
          background-color: #1890ff;
          color: white;
          font-weight: bold;
        }
        
        .current-model {
          background-color: #f9f9f9;
          border: 1px solid #ddd;
          border-radius: 5px;
          padding: 15px;
          margin-bottom: 20px;
        }
        
        .current-model h3 {
          margin-top: 0;
          margin-bottom: 10px;
        }
        
        .model-info {
          display: flex;
          flex-direction: column;
        }
        
        .model-name {
          font-size: 18px;
          font-weight: bold;
        }
        
        .model-path {
          font-size: 14px;
          color: #666;
          margin-top: 5px;
        }
        
        .loading {
          text-align: center;
          padding: 20px;
          color: #666;
        }
        
        .error-message {
          background-color: #fff2f0;
          border: 1px solid #ffccc7;
          color: #ff4d4f;
          padding: 12px;
          border-radius: 4px;
          margin-bottom: 20px;
        }
        
        .models-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 15px;
          margin-bottom: 20px;
        }
        
        .model-card {
          border: 1px solid #ddd;
          border-radius: 5px;
          overflow: hidden;
          transition: transform 0.2s, box-shadow 0.2s;
          cursor: pointer;
        }
        
        .model-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
        }
        
        .model-card.selected {
          border-color: #1890ff;
          box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
        }
        
        .model-image {
          height: 150px;
          background-color: #f0f0f0;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .model-image img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        
        .no-image {
          color: #999;
          font-size: 14px;
        }
        
        .model-card-info {
          padding: 10px;
        }
        
        .model-card-info h4 {
          margin: 0 0 5px 0;
        }
        
        .model-id {
          font-size: 12px;
          color: #666;
        }
        
        .no-models {
          grid-column: 1 / -1;
          padding: 30px;
          text-align: center;
          color: #666;
          border: 1px dashed #ddd;
          border-radius: 5px;
        }
        
        .model-upload {
          margin-top: 30px;
          background-color: #f9f9f9;
          border: 1px solid #ddd;
          border-radius: 5px;
          padding: 15px;
        }
        
        .model-upload h3 {
          margin-top: 0;
        }
        
        .model-upload code {
          background-color: #f0f0f0;
          padding: 2px 5px;
          border-radius: 3px;
          font-family: monospace;
        }
        
        .model-upload a {
          color: #1890ff;
          text-decoration: none;
        }
        
        .model-upload a:hover {
          text-decoration: underline;
        }
      `}</style>
    </div>
  );
};

export default ModelManager; 