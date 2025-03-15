import React from 'react';
import { render, screen, fireEvent, act, waitFor } from '@testing-library/react';
import App from './App';
import * as apiService from './services/api';

// API関数をモック
jest.mock('./services/api', () => ({
  generateManzaiScript: jest.fn(),
  getTimingData: jest.fn()
}));

describe('App 中断・再開機能テスト', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // デフォルトのAPIモック応答
    apiService.generateManzaiScript.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => {
        resolve({
          script: [
            { role: 'tsukkomi', text: 'こんにちは' },
            { role: 'boke', text: 'どうも！' }
          ],
          audio_data: [
            { role: 'tsukkomi', audio_path: '/audio/1.wav' },
            { role: 'boke', audio_path: '/audio/2.wav' }
          ]
        });
      }, 500))
    );
    
    apiService.getTimingData.mockResolvedValue({
      accent_phrases: [{ moras: [{ text: 'こ', start_time: 0, end_time: 100 }] }]
    });
  });
  
  test('生成処理の中断と再開が機能することを確認', async () => {
    render(<App />);
    
    // トピック入力と生成開始
    const input = screen.getByPlaceholderText(/トピックを入力/i) || 
                  screen.getByLabelText(/トピック/i);
    fireEvent.change(input, { target: { value: '中断テスト' } });
    
    const generateButton = screen.getByText(/生成/i);
    fireEvent.click(generateButton);
    
    // 生成中の状態を確認
    expect(await screen.findByText(/生成中/i)).toBeInTheDocument();
    
    // 中断ボタンをクリック
    const cancelButton = screen.getByText(/中断/i) || 
                        screen.getByText(/キャンセル/i);
    fireEvent.click(cancelButton);
    
    // 中断状態の確認
    await waitFor(() => {
      expect(screen.queryByText(/生成中/i)).not.toBeInTheDocument();
    });
    
    // 生成ボタンが再び表示されていることを確認
    expect(screen.getByText(/生成/i)).toBeInTheDocument();
    
    // 再度生成を開始
    fireEvent.click(generateButton);
    
    // 生成が完了し、スクリプトが表示されることを確認
    await waitFor(() => {
      expect(apiService.generateManzaiScript).toHaveBeenCalledTimes(2);
      expect(screen.queryByText(/こんにちは/i)).toBeInTheDocument();
    }, { timeout: 2000 });
  });
  
  test('エラー時に適切に処理されることを確認', async () => {
    // API呼び出しがエラーを返すようにモック
    apiService.generateManzaiScript.mockRejectedValue(new Error('テストエラー'));
    
    render(<App />);
    
    // トピック入力と生成開始
    const input = screen.getByPlaceholderText(/トピックを入力/i) || 
                  screen.getByLabelText(/トピック/i);
    fireEvent.change(input, { target: { value: 'エラーテスト' } });
    
    const generateButton = screen.getByText(/生成/i);
    fireEvent.click(generateButton);
    
    // エラーメッセージが表示されることを確認
    await waitFor(() => {
      expect(screen.queryByText(/エラー/i)).toBeInTheDocument();
    }, { timeout: 2000 });
    
    // 再度生成できることを確認
    expect(screen.getByText(/生成/i)).toBeInTheDocument();
  });
}); 