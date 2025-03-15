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