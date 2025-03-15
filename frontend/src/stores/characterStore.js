/**
 * キャラクター管理ストア
 */
import { useState, useEffect, createContext, useContext } from 'react';
import { getLive2DModels } from '../services/modelService';

// デフォルトの設定
const DEFAULT_CHARACTERS = {
  tsukkomi: {
    id: 'tsukkomi',
    name: 'ツッコミ役',
    modelPath: '/live2d/models/default/model.json',
    type: 'tsukkomi'
  },
  boke: {
    id: 'boke',
    name: 'ボケ役',
    modelPath: '/live2d/models/default/model.json',
    type: 'boke'
  }
};

// コンテキストの作成
const CharacterContext = createContext();

/**
 * キャラクタープロバイダーコンポーネント
 */
export const CharacterProvider = ({ children }) => {
  const [characters, setCharacters] = useState(DEFAULT_CHARACTERS);
  const [activeCharacter, setActiveCharacter] = useState('tsukkomi');
  const [loading, setLoading] = useState(true);
  
  // 初期化時にローカルストレージから設定を読み込む
  useEffect(() => {
    const loadCharacters = async () => {
      try {
        // ローカルストレージから設定を読み込み
        const savedCharacters = localStorage.getItem('characters');
        
        if (savedCharacters) {
          setCharacters(JSON.parse(savedCharacters));
        } else {
          // デフォルト設定を使用
          // 利用可能なモデルを取得して設定
          const models = await getLive2DModels();
          
          if (models.length > 0) {
            const updatedCharacters = { ...DEFAULT_CHARACTERS };
            
            // ツッコミ役のモデルを探す
            const tsukkomiModel = models.find(model => model.type === 'tsukkomi') || models[0];
            if (tsukkomiModel) {
              updatedCharacters.tsukkomi = {
                ...updatedCharacters.tsukkomi,
                id: tsukkomiModel.id,
                name: tsukkomiModel.name,
                modelPath: tsukkomiModel.path
              };
            }
            
            // ボケ役のモデルを探す
            const bokeModel = models.find(model => model.type === 'boke') || 
              (models.length > 1 ? models[1] : models[0]);
            if (bokeModel) {
              updatedCharacters.boke = {
                ...updatedCharacters.boke,
                id: bokeModel.id,
                name: bokeModel.name,
                modelPath: bokeModel.path
              };
            }
            
            setCharacters(updatedCharacters);
            localStorage.setItem('characters', JSON.stringify(updatedCharacters));
          }
        }
      } catch (error) {
        console.error('Failed to load character settings:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadCharacters();
  }, []);
  
  // キャラクターのモデルを変更
  const changeCharacterModel = (character, modelId) => {
    // モデル情報を取得する処理（非同期で行う）
    getLive2DModels().then(models => {
      const model = models.find(m => m.id === modelId);
      
      if (model) {
        const updatedCharacters = {
          ...characters,
          [character]: {
            ...characters[character],
            id: model.id,
            name: model.name,
            modelPath: model.path
          }
        };
        
        setCharacters(updatedCharacters);
        localStorage.setItem('characters', JSON.stringify(updatedCharacters));
      }
    });
  };
  
  // アクティブなキャラクターを切り替え
  const switchActiveCharacter = (character) => {
    setActiveCharacter(character);
  };
  
  return (
    <CharacterContext.Provider value={{
      characters,
      activeCharacter,
      loading,
      changeCharacterModel,
      switchActiveCharacter
    }}>
      {children}
    </CharacterContext.Provider>
  );
};

/**
 * キャラクターストアを使用するためのフック
 */
export const useCharacters = () => {
  const context = useContext(CharacterContext);
  
  if (!context) {
    throw new Error('useCharacters must be used within a CharacterProvider');
  }
  
  return context;
}; 