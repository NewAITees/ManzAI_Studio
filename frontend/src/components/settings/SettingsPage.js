import React, { useState } from 'react';
import ModelManager from './ModelManager';
import PromptEditor from './PromptEditor';

const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('models');
  
  return (
    <div className="settings-page">
      <h1>設定</h1>
      
      <div className="settings-tabs">
        <button
          className={`settings-tab ${activeTab === 'models' ? 'active' : ''}`}
          onClick={() => setActiveTab('models')}
        >
          キャラクターモデル
        </button>
        <button
          className={`settings-tab ${activeTab === 'prompts' ? 'active' : ''}`}
          onClick={() => setActiveTab('prompts')}
        >
          プロンプト設定
        </button>
      </div>
      
      <div className="settings-content">
        {activeTab === 'models' && <ModelManager />}
        {activeTab === 'prompts' && <PromptEditor />}
      </div>
      
      <style jsx>{`
        .settings-page {
          max-width: 1000px;
          margin: 0 auto;
          padding: 20px;
        }
        
        .settings-page h1 {
          margin-bottom: 20px;
          color: #2c3e50;
        }
        
        .settings-tabs {
          display: flex;
          border-bottom: 1px solid #ddd;
          margin-bottom: 20px;
        }
        
        .settings-tab {
          padding: 10px 20px;
          background: none;
          border: none;
          border-bottom: 3px solid transparent;
          cursor: pointer;
          font-size: 16px;
          transition: all 0.2s;
          margin-right: 10px;
        }
        
        .settings-tab:hover {
          color: #3498db;
        }
        
        .settings-tab.active {
          color: #3498db;
          border-bottom-color: #3498db;
          font-weight: bold;
        }
        
        .settings-content {
          background-color: white;
          border-radius: 5px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
          padding: 20px;
        }
      `}</style>
    </div>
  );
};

export default SettingsPage;