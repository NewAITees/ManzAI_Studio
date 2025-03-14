# ManzAI Studio 開発工程書

## 開発ステップ7: モデル管理とプロンプトカスタマイズ機能の実装

### Live2Dモデルの自動検出機能

1. **モデル検出APIエンドポイントの実装**
   ```bash
   # Live2Dモデルを検出するAPIエンドポイントを追加
   cat > src/backend/app/routes/models.py << 'EOF'
   """Model management routes."""
   from flask import Blueprint, jsonify, current_app, request
   from typing import Dict, Any, List
   import os
   import json
   import glob
   
   from backend.app.utils.error_handlers import api_error_handler, APIError
   
   bp = Blueprint("models", __name__, url_prefix="/api/models")
   
   # モデルディレクトリパス（開発環境と本番環境で異なる可能性あり）
   LIVE2D_BASE_DIR = os.path.join(os.getcwd(), "frontend", "public", "live2d", "models")
   
   
   @bp.route("/live2d", methods=["GET"])
   @api_error_handler
   def get_live2d_models() -> Dict[str, Any]:
       """Get available Live2D models.
       
       Returns:
           Dict containing models list.
       """
       try:
           # モデルディレクトリの存在確認
           if not os.path.exists(LIVE2D_BASE_DIR):
               return jsonify({
                   "models": [],
                   "message": "モデルディレクトリが存在しません。"
               })
           
           # モデルを検索
           models = []
           for model_dir in glob.glob(os.path.join(LIVE2D_BASE_DIR, "*/")):
               model_name = os.path.basename(os.path.dirname(model_dir))
               
               # model.json ファイルの検索
               model_json_path = os.path.join(model_dir, "model.json")
               
               if os.path.exists(model_json_path):
                   try:
                       with open(model_json_path, 'r', encoding='utf-8') as f:
                           model_data = json.load(f)
                           
                       # モデル情報を構築
                       model_info = {
                           "id": model_name,
                           "name": model_data.get("name", model_name),
                           "path": f"/live2d/models/{model_name}/model.json",
                           "type": model_data.get("type", "unknown"),
                           "thumbnail": f"/live2d/models/{model_name}/thumbnail.png" if os.path.exists(os.path.join(model_dir, "thumbnail.png")) else None
                       }
                       
                       models.append(model_info)
                   except json.JSONDecodeError:
                       # JSON解析エラーは無視してスキップ
                       continue
           
           return jsonify({
               "models": models
           })
       except Exception as e:
           raise APIError(f"モデル一覧の取得中にエラーが発生しました: {str(e)}", 500)
   
   
   @bp.route("/live2d/register", methods=["POST"])
   @api_error_handler
   def register_model() -> Dict[str, Any]:
       """Register a new Live2D model with metadata.
       
       Returns:
           Dict containing registration result.
       """
       data = request.get_json()
       if not data or "id" not in data or "path" not in data:
           raise APIError("モデルIDとパスが必要です", 400)
           
       model_id = data["id"]
       model_path = data["path"]
       
       # モデルディレクトリの作成
       model_dir = os.path.join(LIVE2D_BASE_DIR, model_id)
       os.makedirs(model_dir, exist_ok=True)
       
       # メタデータの作成
       metadata = {
           "name": data.get("name", model_id),
           "type": data.get("type", "character"),
           "model": os.path.basename(model_path),
           "textures": data.get("textures", []),
           "version": "1.0.0"
       }
       
       # メタデータをファイルに保存
       with open(os.path.join(model_dir, "model.json"), 'w', encoding='utf-8') as f:
           json.dump(metadata, f, ensure_ascii=False, indent=2)
       
       return jsonify({
           "success": True,
           "message": f"モデル {model_id} が登録されました",
           "model": {
               "id": model_id,
               "name": metadata["name"],
               "path": f"/live2d/models/{model_id}/model.json",
               "type": metadata["type"]
           }
       })
   EOF
   ```

2. **モデルAPIをFlaskアプリに登録**
   ```bash
   # app/__init__.pyを更新してモデルAPIを登録
   # 以下のimportとregister_blueprintの部分を追加
   
   # __init__.pyの更新箇所だけを示す（残りの部分は同じ）
   # 既存のimportと設定部分は変更せず、以下のように追加
   
   # Register blueprints
   from backend.app.routes import api, models  # modelsを追加
   app.register_blueprint(api.bp)
   app.register_blueprint(models.bp)  # これを追加
   ```

3. **フロントエンドモデル管理サービスの作成**
   ```bash
   # モデル管理サービスの作成
   cat > frontend/src/services/modelService.js << 'EOF'
   /**
    * モデル管理サービス
    */
   import axios from 'axios';
   
   const API_URL = '/api/models';
   
   /**
    * Live2Dモデル一覧を取得
    */
   export const getLive2DModels = async () => {
     try {
       const response = await axios.get(`${API_URL}/live2d`);
       return response.data.models || [];
     } catch (error) {
       console.error('Failed to get Live2D models:', error);
       throw error;
     }
   };
   
   /**
    * Live2Dモデルを登録
    */
   export const registerLive2DModel = async (modelData) => {
     try {
       const response = await axios.post(`${API_URL}/live2d/register`, modelData);
       return response.data;
     } catch (error) {
       console.error('Failed to register Live2D model:', error);
       throw error;
     }
   };
   EOF
   ```

### プロンプトカスタマイズ機能

1. **プロンプト管理APIの実装**
   ```bash
   # プロンプト管理APIエンドポイントを追加
   cat > src/backend/app/routes/prompts.py << 'EOF'
   """Prompt management routes."""
   from flask import Blueprint, jsonify, request, current_app
   from typing import Dict, Any, List
   import os
   import json
   
   from backend.app.utils.error_handlers import api_error_handler, APIError
   
   bp = Blueprint("prompts", __name__, url_prefix="/api/prompts")
   
   # プロンプトディレクトリパス
   PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
   
   
   @bp.route("", methods=["GET"])
   @api_error_handler
   def get_prompts() -> Dict[str, Any]:
       """Get available prompt templates.
       
       Returns:
           Dict containing prompts list.
       """
       try:
           prompts = []
           
           # プロンプトディレクトリの存在確認
           if not os.path.exists(PROMPT_DIR):
               return jsonify({
                   "prompts": [],
                   "message": "プロンプトディレクトリが存在しません。"
               })
           
           # プロンプト一覧を取得
           for filename in os.listdir(PROMPT_DIR):
               if filename.endswith(".txt"):
                   prompt_id = filename[:-4]
                   
                   # メタデータファイルを探す
                   metadata_path = os.path.join(PROMPT_DIR, f"{prompt_id}.meta.json")
                   metadata = {}
                   
                   if os.path.exists(metadata_path):
                       try:
                           with open(metadata_path, 'r', encoding='utf-8') as f:
                               metadata = json.load(f)
                       except json.JSONDecodeError:
                           pass
                   
                   # プロンプトファイルを読み込む
                   with open(os.path.join(PROMPT_DIR, filename), 'r', encoding='utf-8') as f:
                       content = f.read()
                   
                   prompt_info = {
                       "id": prompt_id,
                       "name": metadata.get("name", prompt_id),
                       "description": metadata.get("description", ""),
                       "content": content,
                       "parameters": metadata.get("parameters", []),
                       "isDefault": metadata.get("isDefault", False)
                   }
                   
                   prompts.append(prompt_info)
           
           return jsonify({
               "prompts": prompts
           })
       except Exception as e:
           raise APIError(f"プロンプト一覧の取得中にエラーが発生しました: {str(e)}", 500)
   
   
   @bp.route("/<prompt_id>", methods=["GET"])
   @api_error_handler
   def get_prompt(prompt_id: str) -> Dict[str, Any]:
       """Get a specific prompt template.
       
       Args:
           prompt_id: ID of the prompt template.
           
       Returns:
           Dict containing prompt information.
       """
       try:
           # プロンプトファイルパス
           prompt_path = os.path.join(PROMPT_DIR, f"{prompt_id}.txt")
           
           if not os.path.exists(prompt_path):
               raise APIError(f"プロンプト {prompt_id} が見つかりません", 404)
           
           # メタデータファイルを探す
           metadata_path = os.path.join(PROMPT_DIR, f"{prompt_id}.meta.json")
           metadata = {}
           
           if os.path.exists(metadata_path):
               try:
                   with open(metadata_path, 'r', encoding='utf-8') as f:
                       metadata = json.load(f)
               except json.JSONDecodeError:
                   pass
           
           # プロンプトファイルを読み込む
           with open(prompt_path, 'r', encoding='utf-8') as f:
               content = f.read()
           
           prompt_info = {
               "id": prompt_id,
               "name": metadata.get("name", prompt_id),
               "description": metadata.get("description", ""),
               "content": content,
               "parameters": metadata.get("parameters", []),
               "isDefault": metadata.get("isDefault", False)
           }
           
           return jsonify(prompt_info)
       except APIError:
           raise
       except Exception as e:
           raise APIError(f"プロンプトの取得中にエラーが発生しました: {str(e)}", 500)
   
   
   @bp.route("", methods=["POST"])
   @api_error_handler
   def create_prompt() -> Dict[str, Any]:
       """Create a new prompt template.
       
       Returns:
           Dict containing creation result.
       """
       data = request.get_json()
       if not data or "id" not in data or "content" not in data:
           raise APIError("プロンプトIDと内容が必要です", 400)
           
       prompt_id = data["id"]
       content = data["content"]
       
       # プロンプトファイルパス
       prompt_path = os.path.join(PROMPT_DIR, f"{prompt_id}.txt")
       
       # 既存のプロンプトを上書きしないよう確認
       if os.path.exists(prompt_path) and not data.get("overwrite", False):
           raise APIError(f"プロンプト {prompt_id} は既に存在します", 409)
       
       # プロンプト内容を保存
       with open(prompt_path, 'w', encoding='utf-8') as f:
           f.write(content)
       
       # メタデータを保存
       metadata = {
           "name": data.get("name", prompt_id),
           "description": data.get("description", ""),
           "parameters": data.get("parameters", []),
           "isDefault": data.get("isDefault", False)
       }
       
       with open(os.path.join(PROMPT_DIR, f"{prompt_id}.meta.json"), 'w', encoding='utf-8') as f:
           json.dump(metadata, f, ensure_ascii=False, indent=2)
       
       return jsonify({
           "success": True,
           "message": f"プロンプト {prompt_id} が作成されました",
           "prompt": {
               "id": prompt_id,
               "name": metadata["name"],
               "description": metadata["description"],
               "content": content,
               "parameters": metadata["parameters"],
               "isDefault": metadata["isDefault"]
           }
       })
   
   
   @bp.route("/<prompt_id>", methods=["PUT"])
   @api_error_handler
   def update_prompt(prompt_id: str) -> Dict[str, Any]:
       """Update a prompt template.
       
       Args:
           prompt_id: ID of the prompt template to update.
           
       Returns:
           Dict containing update result.
       """
       data = request.get_json()
       if not data or "content" not in data:
           raise APIError("プロンプト内容が必要です", 400)
           
       content = data["content"]
       
       # プロンプトファイルパス
       prompt_path = os.path.join(PROMPT_DIR, f"{prompt_id}.txt")
       
       # プロンプトの存在確認
       if not os.path.exists(prompt_path):
           raise APIError(f"プロンプト {prompt_id} が見つかりません", 404)
       
       # プロンプト内容を保存
       with open(prompt_path, 'w', encoding='utf-8') as f:
           f.write(content)
       
       # メタデータを更新
       metadata_path = os.path.join(PROMPT_DIR, f"{prompt_id}.meta.json")
       
       # 既存のメタデータを読み込む
       existing_metadata = {}
       if os.path.exists(metadata_path):
           try:
               with open(metadata_path, 'r', encoding='utf-8') as f:
                   existing_metadata = json.load(f)
           except json.JSONDecodeError:
               pass
       
       # メタデータを更新
       metadata = {
           "name": data.get("name", existing_metadata.get("name", prompt_id)),
           "description": data.get("description", existing_metadata.get("description", "")),
           "parameters": data.get("parameters", existing_metadata.get("parameters", [])),
           "isDefault": data.get("isDefault", existing_metadata.get("isDefault", False))
       }
       
       with open(metadata_path, 'w', encoding='utf-8') as f:
           json.dump(metadata, f, ensure_ascii=False, indent=2)
       
       return jsonify({
           "success": True,
           "message": f"プロンプト {prompt_id} が更新されました",
           "prompt": {
               "id": prompt_id,
               "name": metadata["name"],
               "description": metadata["description"],
               "content": content,
               "parameters": metadata["parameters"],
               "isDefault": metadata["isDefault"]
           }
       })
   
   
   @bp.route("/<prompt_id>", methods=["DELETE"])
   @api_error_handler
   def delete_prompt(prompt_id: str) -> Dict[str, Any]:
       """Delete a prompt template.
       
       Args:
           prompt_id: ID of the prompt template to delete.
           
       Returns:
           Dict containing deletion result.
       """
       # デフォルトプロンプトは削除できない
       if prompt_id == "manzai_prompt":
           raise APIError("デフォルトプロンプトは削除できません", 403)
       
       # プロンプトファイルパス
       prompt_path = os.path.join(PROMPT_DIR, f"{prompt_id}.txt")
       metadata_path = os.path.join(PROMPT_DIR, f"{prompt_id}.meta.json")
       
       # プロンプトの存在確認
       if not os.path.exists(prompt_path):
           raise APIError(f"プロンプト {prompt_id} が見つかりません", 404)
       
       # ファイルの削除
       try:
           os.remove(prompt_path)
           if os.path.exists(metadata_path):
               os.remove(metadata_path)
       except Exception as e:
           raise APIError(f"プロンプトの削除中にエラーが発生しました: {str(e)}", 500)
       
       return jsonify({
           "success": True,
           "message": f"プロンプト {prompt_id} が削除されました"
       })
   EOF
   ```

2. **プロンプトAPIをFlaskアプリに登録**
   ```bash
   # app/__init__.pyを更新してプロンプトAPIを登録
   # 以下のimportとregister_blueprintの部分を追加
   
   # __init__.pyの更新箇所だけを示す（残りの部分は同じ）
   # 既存のimportと設定部分は変更せず、以下のように追加
   
   # Register blueprints
   from backend.app.routes import api, models, prompts  # promptsを追加
   app.register_blueprint(api.bp)
   app.register_blueprint(models.bp)
   app.register_blueprint(prompts.bp)  # これを追加
   ```

3. **フロントエンドプロンプト管理サービスの作成**
   ```bash
   # プロンプト管理サービスの作成
   cat > frontend/src/services/promptService.js << 'EOF'
   /**
    * プロンプト管理サービス
    */
   import axios from 'axios';
   
   const API_URL = '/api/prompts';
   
   /**
    * プロンプト一覧を取得
    */
   export const getPrompts = async () => {
     try {
       const response = await axios.get(API_URL);
       return response.data.prompts || [];
     } catch (error) {
       console.error('Failed to get prompts:', error);
       throw error;
     }
   };
   
   /**
    * 特定のプロンプトを取得
    */
   export const getPrompt = async (promptId) => {
     try {
       const response = await axios.get(`${API_URL}/${promptId}`);
       return response.data;
     } catch (error) {
       console.error(`Failed to get prompt ${promptId}:`, error);
       throw error;
     }
   };
   
   /**
    * 新しいプロンプトを作成
    */
   export const createPrompt = async (promptData) => {
     try {
       const response = await axios.post(API_URL, promptData);
       return response.data;
     } catch (error) {
       console.error('Failed to create prompt:', error);
       throw error;
     }
   };
   
   /**
    * プロンプトを更新
    */
   export const updatePrompt = async (promptId, promptData) => {
     try {
       const response = await axios.put(`${API_URL}/${promptId}`, promptData);
       return response.data;
     } catch (error) {
       console.error(`Failed to update prompt ${promptId}:`, error);
       throw error;
     }
   };
   
   /**
    * プロンプトを削除
    */
   export const deletePrompt = async (promptId) => {
     try {
       const response = await axios.delete(`${API_URL}/${promptId}`);
       return response.data;
     } catch (error) {
       console.error(`Failed to delete prompt ${promptId}:`, error);
       throw error;
     }
   };
   EOF
   ```

### プロンプト設定UIの実装

1. **プロンプト編集コンポーネントの作成**
   ```bash
   # プロンプト編集コンポーネントを作成
   mkdir -p frontend/src/components/settings
   cat > frontend/src/components/settings/PromptEditor.js << 'EOF'
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
   EOF
   ```

### モデル設定UIの実装

1. **モデル管理コンポーネントの作成**
   ```bash
   # モデル管理コンポーネントを作成
   cat > frontend/src/components/settings/ModelManager.js << 'EOF'
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
   EOF
   ```

2. **メタデータファイル用のスクリプトの作成**
   ```bash
   # モデルメタデータ作成用のスクリプトを追加
   mkdir -p scripts
   cat > scripts/create_model_metadata.js << 'EOF'
   /**
    * Live2Dモデル用のメタデータファイル作成スクリプト
    * 
    * 使用方法:
    *   node scripts/create_model_metadata.js
    */
   
   const fs = require('fs');
   const path = require('path');
   const readline = require('readline');
   
   const rl = readline.createInterface({
     input: process.stdin,
     output: process.stdout
   });
   
   // モデルディレクトリパス
   const MODELS_DIR = path.join(__dirname, '..', 'frontend', 'public', 'live2d', 'models');
   
   // モデルの種類
   const MODEL_TYPES = ['tsukkomi', 'boke', 'unknown'];
   
   // プロンプト関数
   const prompt = (question) => {
     return new Promise((resolve) => {
       rl.question(question, (answer) => {
         resolve(answer);
       });
     });
   };
   
   // メインプロセス
   const main = async () => {
     try {
       console.log('Live2Dモデルメタデータ作成ツール');
       console.log('=================================');
       
       // モデルディレクトリの存在確認
       if (!fs.existsSync(MODELS_DIR)) {
         console.error(`モデルディレクトリが見つかりません: ${MODELS_DIR}`);
         return;
       }
       
       // モデルディレクトリ一覧を取得
       const modelDirs = fs.readdirSync(MODELS_DIR, { withFileTypes: true })
         .filter(dirent => dirent.isDirectory())
         .map(dirent => dirent.name);
       
       if (modelDirs.length === 0) {
         console.log('モデルディレクトリが見つかりません。');
         return;
       }
       
       console.log('利用可能なモデルディレクトリ:');
       modelDirs.forEach((dir, index) => {
         console.log(`  ${index + 1}. ${dir}`);
       });
       
       // モデルの選択
       const modelIndexStr = await prompt('処理するモデルの番号を入力してください: ');
       const modelIndex = parseInt(modelIndexStr, 10) - 1;
       
       if (isNaN(modelIndex) || modelIndex < 0 || modelIndex >= modelDirs.length) {
         console.error('無効な番号です。');
         return;
       }
       
       const modelDir = modelDirs[modelIndex];
       const modelPath = path.join(MODELS_DIR, modelDir);
       
       console.log(`\n"${modelDir}" のメタデータを作成します。`);
       
       // model3.jsonファイルを検索
       const modelFiles = fs.readdirSync(modelPath)
         .filter(file => file.endsWith('.model3.json'));
       
       if (modelFiles.length === 0) {
         console.error('model3.jsonファイルが見つかりません。');
         return;
       }
       
       // model3.jsonファイルの選択
       let modelFile;
       if (modelFiles.length === 1) {
         modelFile = modelFiles[0];
         console.log(`モデルファイル: ${modelFile}`);
       } else {
         console.log('利用可能なモデルファイル:');
         modelFiles.forEach((file, index) => {
           console.log(`  ${index + 1}. ${file}`);
         });
         
         const fileIndexStr = await prompt('使用するモデルファイルの番号を入力してください: ');
         const fileIndex = parseInt(fileIndexStr, 10) - 1;
         
         if (isNaN(fileIndex) || fileIndex < 0 || fileIndex >= modelFiles.length) {
           console.error('無効な番号です。');
           return;
         }
         
         modelFile = modelFiles[fileIndex];
       }
       
       // テクスチャファイルを検索
       const textureFiles = fs.readdirSync(modelPath)
         .filter(file => file.endsWith('.png') || file.endsWith('.jpg') || file.endsWith('.jpeg'));
       
       // メタデータの入力
       const name = await prompt('モデル名を入力してください: ');
       
       console.log('\nモデルの種類:');
       MODEL_TYPES.forEach((type, index) => {
         console.log(`  ${index + 1}. ${type}`);
       });
       
       const typeIndexStr = await prompt('モデルの種類の番号を入力してください: ');
       const typeIndex = parseInt(typeIndexStr, 10) - 1;
       
       if (isNaN(typeIndex) || typeIndex < 0 || typeIndex >= MODEL_TYPES.length) {
         console.error('無効な番号です。');
         return;
       }
       
       const type = MODEL_TYPES[typeIndex];
       
       // メタデータの作成
       const metadata = {
         name,
         type,
         model: modelFile,
         textures: textureFiles,
         version: "1.0.0"
       };
       
       // メタデータの保存
       const metadataPath = path.join(modelPath, 'model.json');
       fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2), 'utf8');
       
       console.log(`\nメタデータが作成されました: ${metadataPath}`);
       
       // サムネイル確認
       const thumbnailPath = path.join(modelPath, 'thumbnail.png');
       if (!fs.existsSync(thumbnailPath)) {
         console.log('\n警告: サムネイル画像 (thumbnail.png) が見つかりません。');
         console.log('サムネイル画像を追加すると、モデル選択画面でモデルを視覚的に識別できます。');
       }
     } catch (error) {
       console.error('エラーが発生しました:', error);
     } finally {
       rl.close();
     }
   };
   
   main();
   EOF
   ```

3. **モデル設定ドキュメントの作成**
   ```bash
   # モデル設定ガイドを作成
   mkdir -p docs
   cat > docs/model_setup.md << 'EOF'
   # Live2Dモデル設定ガイド

   このガイドでは、ManzAI Studioでカスタム Live2D モデルを使用するための設定方法を説明します。

   ## 必要なファイル

   Live2D モデルには、以下のファイルが必要です：

   - `.model3.json` ファイル (Live2D Cubism 3.x 形式)
   - テクスチャファイル (通常は PNG)
   - `model.json` (メタデータファイル)
   - `thumbnail.png` (オプション、サムネイル画像)

   ## モデルの配置

   1. モデル用のディレクトリを作成します：
      ```
      frontend/public/live2d/models/[モデル名]/
      ```

   2. モデルファイル (`.model3.json`) とテクスチャファイルをディレクトリに配置します

   3. `thumbnail.png` ファイルを追加します (推奨サイズ: 200x150px)

   ## メタデータファイルの作成

   各モデルには `model.json` メタデータファイルが必要です。このファイルはモデル情報を保持します。

   ### 自動作成 (推奨)

   提供されているスクリプトを使用して、メタデータファイルを簡単に作成できます：

   ```bash
   node scripts/create_model_metadata.js
   ```

   画面の指示に従って操作してください。

   ### 手動作成

   以下の内容で `model.json` ファイルを手動で作成することもできます：

   ```json
   {
     "name": "モデル名",
     "type": "tsukkomi", // "tsukkomi", "boke", または "unknown"
     "model": "model3.json", // モデルファイル名
     "textures": ["texture.png"], // テクスチャファイル名の配列
     "version": "1.0.0"
   }
   ```

   ## モデルの種類

   モデルには以下の種類があります：

   - `tsukkomi`: ツッコミ役用モデル (左側に表示)
   - `boke`: ボケ役用モデル (右側に表示)
   - `unknown`: どちらの役にも使用可能

   ## 互換性のあるモデルの入手先

   無料または商用利用可能な Live2D モデルは以下から入手できます：

   - [Live2D Cubism 公式サンプルモデル](https://www.live2d.com/download/sample-data/)
   - [VRoid Hub](https://hub.vroid.com/) (モデルによってライセンスが異なるので注意)
   - 各種 Live2D モデル配布サイト

   モデルを使用する際は、必ずライセンスを確認し、条件を遵守してください。

   ## トラブルシューティング

   ### モデルが表示されない

   - メタデータファイル `model.json` が正しく作成されているか確認
   - モデルファイル (`.model3.json`) とテクスチャファイルのパスが正しいか確認
   - ブラウザの開発者ツールでエラーメッセージを確認

   ### モデルの位置がおかしい

   - モデルの種類 (`type`) が適切に設定されているか確認
   - キャラクター設定でモデルが正しく割り当てられているか確認
   EOF
   ```

### 設定メニューの統合

1. **設定ページコンポーネントの作成**
   ```bash
   # 設定ページコンポーネントを作成
   cat > frontend/src/components/settings/SettingsPage.js << 'EOF'
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
   EOF
   ```

2. **Appコンポーネントを更新して設定ページを統合**
   ```bash
   # App.jsを更新して設定ページを統合
   cat > frontend/src/App.js << 'EOF'
   import React, { useState } from 'react';
   import './App.css';
   import ManzaiGenerator from './components/ManzaiGenerator';
   import Live2DStage from './components/Live2DStage';
   import SettingsPage from './components/settings/SettingsPage';
   import { CharacterProvider } from './stores/characterStore';
   
   function App() {
     const [script, setScript] = useState([]);
     const [audioData, setAudioData] = useState([]);
     const [isLoading, setIsLoading] = useState(false);
     const [error, setError] = useState(null);
     const [showSettings, setShowSettings] = useState(false);
     
     const toggleSettings = () => {
       setShowSettings(!showSettings);
     };
     
     return (
       <CharacterProvider>
         <div className="App">
           <header className="App-header">
             <h1>ManzAI Studio</h1>
             <p>ローカルで動作する漫才生成・実演Webアプリケーション</p>
             <button
               className="settings-button"
               onClick={toggleSettings}
             >
               {showSettings ? 'ホームに戻る' : '設定'}
             </button>
           </header>
           
           <main className="App-main">
             {showSettings ? (
               <SettingsPage />
             ) : (
               <>
                 <div className="stage-container">
                   <Live2DStage 
                     script={script} 
                     audioData={audioData} 
                   />
                 </div>
                 
                 <div className="control-container">
                   <ManzaiGenerator 
                     onScriptGenerated={(script, audioData) => {
                       setScript(script);
                       setAudioData(audioData);
                     }}
                     isLoading={isLoading}
                     setIsLoading={setIsLoading}
                     error={error}
                     setError={setError}
                   />
                 </div>
               </>
             )}
           </main>
           
           <footer className="App-footer">
             <p>© 2025 ManzAI Studio</p>
           </footer>
         </div>
       </CharacterProvider>
     );
   }
   
   export default App;
   EOF
   ```

3. **CSS更新**
   ```bash
   # App.cssを更新して設定ボタンのスタイルを追加
   # 既存のApp.cssファイルの末尾に以下を追加

   # 以下のコードを既存のApp.cssの適切な場所に追加
   cat >> frontend/src/App.css << 'EOF'
   /* 設定ボタンスタイル */
   .settings-button {
     position: absolute;
     right: 20px;
     top: 20px;
     background-color: rgba(255, 255, 255, 0.2);
     color: white;
     border: none;
     padding: 8px 15px;
     border-radius: 5px;
     cursor: pointer;
     font-size: 14px;
     transition: background-color 0.3s;
   }
   
   .settings-button:hover {
     background-color: rgba(255, 255, 255, 0.3);
   }
   EOF
   ```

この開発ステップでは、以下の機能を実装しました：

1. Live2Dモデルの自動検出と管理機能
2. モデル設定用のユーザーインターフェース
3. プロンプトのカスタマイズと管理機能
4. 設定ページの統合

これらの機能により、ユーザーは自分の好みに合わせてアプリケーションをカスタマイズできるようになりました。また、モデル設定ガイドやメタデータ作成スクリプトを提供することで、ユーザーが独自のLive2Dモデルを簡単に追加できるようになっています。次のステップでは、システム全体の安定性テストとパフォーマンス最適化を行います。