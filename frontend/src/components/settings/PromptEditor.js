import React, { useState, useEffect } from 'react';
import { getPrompts, getPrompt, updatePrompt, createPrompt, deletePrompt } from '../../services/promptService';

const PromptEditor = () => {
  const [prompts, setPrompts] = useState([]);
  const [selectedPromptId, setSelectedPromptId] = useState('');
  const [promptData, setPromptData] = useState({
    id: '',
    name: '',
    description: '',
    content: '',
    parameters: []
  });
  const [isEditing, setIsEditing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // プロンプト一覧を取得
  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        const promptsList = await getPrompts();
        setPrompts(promptsList);
        
        // デフォルトプロンプトを選択
        const defaultPrompt = promptsList.find(p => p.isDefault) || promptsList[0];
        if (defaultPrompt) {
          setSelectedPromptId(defaultPrompt.id);
          setPromptData(defaultPrompt);
        }
      } catch (err) {
        setError('プロンプト一覧の取得に失敗しました');
        console.error(err);
      }
    };
    
    fetchPrompts();
  }, []);
  
  // プロンプトを選択
  const handleSelectPrompt = async (promptId) => {
    try {
      setError('');
      setSuccess('');
      
      if (promptId === 'new') {
        // 新規作成モード
        setIsCreating(true);
        setIsEditing(true);
        setSelectedPromptId('new');
        setPromptData({
          id: '',
          name: '',
          description: '',
          content: '',
          parameters: []
        });
      } else {
        // 既存プロンプトの編集
        setIsCreating(false);
        const prompt = await getPrompt(promptId);
        setSelectedPromptId(promptId);
        setPromptData(prompt);
        setIsEditing(false);
      }
    } catch (err) {
      setError('プロンプトの読み込みに失敗しました');
      console.error(err);
    }
  };
  
  // フォーム入力の処理
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setPromptData({
      ...promptData,
      [name]: value
    });
  };
  
  // プロンプトの保存
  const handleSavePrompt = async () => {
    try {
      setError('');
      setSuccess('');
      
      // 入力検証
      if (!promptData.id && isCreating) {
        setError('プロンプトIDを入力してください');
        return;
      }
      
      if (!promptData.name) {
        setError('プロンプト名を入力してください');
        return;
      }
      
      if (!promptData.content) {
        setError('プロンプト内容を入力してください');
        return;
      }
      
      if (isCreating) {
        // 新規作成
        await createPrompt(promptData);
        setSuccess('プロンプトが作成されました');
        
        // プロンプト一覧を更新
        const promptsList = await getPrompts();
        setPrompts(promptsList);
        
        // 作成したプロンプトを選択
        setSelectedPromptId(promptData.id);
        setIsCreating(false);
      } else {
        // 更新
        await updatePrompt(selectedPromptId, promptData);
        setSuccess('プロンプトが更新されました');
        
        // プロンプト一覧を更新
        const promptsList = await getPrompts();
        setPrompts(promptsList);
      }
      
      setIsEditing(false);
    } catch (err) {
      setError('プロンプトの保存に失敗しました');
      console.error(err);
    }
  };
  
  // プロンプトの削除
  const handleDeletePrompt = async () => {
    if (!window.confirm('このプロンプトを削除してもよろしいですか？')) {
      return;
    }
    
    try {
      setError('');
      setSuccess('');
      
      await deletePrompt(selectedPromptId);
      setSuccess('プロンプトが削除されました');
      
      // プロンプト一覧を更新
      const promptsList = await getPrompts();
      setPrompts(promptsList);
      
      // デフォルトプロンプトを選択
      const defaultPrompt = promptsList.find(p => p.isDefault) || promptsList[0];
      if (defaultPrompt) {
        setSelectedPromptId(defaultPrompt.id);
        setPromptData(defaultPrompt);
      }
      
      setIsEditing(false);
      setIsCreating(false);
    } catch (err) {
      setError('プロンプトの削除に失敗しました');
      console.error(err);
    }
  };
  
  return (
    <div className="prompt-editor">
      <h2>プロンプト設定</h2>
      
      <div className="prompt-editor-container">
        <div className="prompt-list">
          <h3>プロンプト一覧</h3>
          <ul>
            {prompts.map(prompt => (
              <li 
                key={prompt.id} 
                className={selectedPromptId === prompt.id ? 'selected' : ''}
                onClick={() => handleSelectPrompt(prompt.id)}
              >
                {prompt.name}
                {prompt.isDefault && <span className="default-badge">デフォルト</span>}
              </li>
            ))}
            <li 
              className={selectedPromptId === 'new' ? 'selected new-prompt' : 'new-prompt'}
              onClick={() => handleSelectPrompt('new')}
            >
              + 新規プロンプト
            </li>
          </ul>
        </div>
        
        <div className="prompt-detail">
          <h3>{isCreating ? '新規プロンプト作成' : 'プロンプト詳細'}</h3>
          
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}
          
          <form onSubmit={(e) => { e.preventDefault(); handleSavePrompt(); }}>
            {isCreating && (
              <div className="form-group">
                <label htmlFor="id">プロンプトID:</label>
                <input
                  type="text"
                  id="id"
                  name="id"
                  value={promptData.id}
                  onChange={handleInputChange}
                  disabled={!isCreating}
                  required
                />
                <small>英数字とアンダースコアのみ使用可能</small>
              </div>
            )}
            
            <div className="form-group">
              <label htmlFor="name">プロンプト名:</label>
              <input
                type="text"
                id="name"
                name="name"
                value={promptData.name}
                onChange={handleInputChange}
                disabled={!isEditing && !isCreating}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="description">説明:</label>
              <input
                type="text"
                id="description"
                name="description"
                value={promptData.description}
                onChange={handleInputChange}
                disabled={!isEditing && !isCreating}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="content">プロンプト内容:</label>
              <textarea
                id="content"
                name="content"
                value={promptData.content}
                onChange={handleInputChange}
                disabled={!isEditing && !isCreating}
                rows="12"
                required
              />
              <small>
                {{topic}} のような記法でパラメータを指定できます。<br />
                例: 「トピック: {{topic}}」
              </small>
            </div>
            
            <div className="button-group">
              {isEditing || isCreating ? (
                <>
                  <button 
                    type="submit" 
                    className="save-button"
                  >
                    保存
                  </button>
                  <button 
                    type="button" 
                    className="cancel-button"
                    onClick={() => {
                      if (isCreating) {
                        handleSelectPrompt(prompts[0]?.id || '');
                      } else {
                        setIsEditing(false);
                        handleSelectPrompt(selectedPromptId);
                      }
                    }}
                  >
                    キャンセル
                  </button>
                </>
              ) : (
                <>
                  <button 
                    type="button" 
                    className="edit-button"
                    onClick={() => setIsEditing(true)}
                  >
                    編集
                  </button>
                  {!promptData.isDefault && (
                    <button 
                      type="button" 
                      className="delete-button"
                      onClick={handleDeletePrompt}
                    >
                      削除
                    </button>
                  )}
                </>
              )}
            </div>
          </form>
        </div>
      </div>
      
      <style jsx>{`
        .prompt-editor {
          margin-top: 20px;
        }
        
        .prompt-editor-container {
          display: flex;
          gap: 20px;
          margin-top: 20px;
        }
        
        .prompt-list {
          flex: 0 0 250px;
          border: 1px solid #ddd;
          border-radius: 5px;
          padding: 15px;
        }
        
        .prompt-list h3 {
          margin-top: 0;
          padding-bottom: 10px;
          border-bottom: 1px solid #eee;
        }
        
        .prompt-list ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }
        
        .prompt-list li {
          padding: 10px;
          border-radius: 5px;
          margin-bottom: 5px;
          cursor: pointer;
          transition: background-color 0.2s;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .prompt-list li:hover {
          background-color: #f0f0f0;
        }
        
        .prompt-list li.selected {
          background-color: #e6f7ff;
          border-left: 3px solid #1890ff;
        }
        
        .prompt-list li.new-prompt {
          color: #1890ff;
        }
        
        .default-badge {
          font-size: 10px;
          background-color: #1890ff;
          color: white;
          padding: 2px 5px;
          border-radius: 10px;
        }
        
        .prompt-detail {
          flex: 1;
          border: 1px solid #ddd;
          border-radius: 5px;
          padding: 15px;
        }
        
        .prompt-detail h3 {
          margin-top: 0;
          padding-bottom: 10px;
          border-bottom: 1px solid #eee;
        }
        
        .form-group {
          margin-bottom: 15px;
        }
        
        .form-group label {
          display: block;
          font-weight: bold;
          margin-bottom: 5px;
        }
        
        .form-group input,
        .form-group textarea {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 14px;
        }
        
        .form-group small {
          display: block;
          color: #666;
          font-size: 12px;
          margin-top: 5px;
        }
        
        .button-group {
          display: flex;
          gap: 10px;
          margin-top: 20px;
        }
        
        button {
          padding: 8px 15px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: bold;
        }
        
        .save-button {
          background-color: #1890ff;
          color: white;
        }
        
        .cancel-button {
          background-color: #f0f0f0;
          color: #333;
        }
        
        .edit-button {
          background-color: #52c41a;
          color: white;
        }
        
        .delete-button {
          background-color: #ff4d4f;
          color: white;
        }
        
        .error-message {
          background-color: #fff2f0;
          border: 1px solid #ffccc7;
          color: #ff4d4f;
          padding: 8px 12px;
          border-radius: 4px;
          margin-bottom: 15px;
        }
        
        .success-message {
          background-color: #f6ffed;
          border: 1px solid #b7eb8f;
          color: #52c41a;
          padding: 8px 12px;
          border-radius: 4px;
          margin-bottom: 15px;
        }
      `}</style>
    </div>
  );
};

export default PromptEditor; 