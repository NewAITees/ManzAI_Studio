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