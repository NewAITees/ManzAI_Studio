import { openDisplayWindow, sendStateToDisplayWindow } from './windowManager';

describe('windowManager', () => {
  let mockWindow;
  let originalWindow;
  
  beforeEach(() => {
    // 元のwindowオブジェクトを保存
    originalWindow = global.window;
    
    // windowオブジェクトのモック
    mockWindow = {
      postMessage: jest.fn()
    };
  });
  
  afterEach(() => {
    // テスト後に元のwindowオブジェクトを復元
    global.window = originalWindow;
  });

  test('opens display window and returns window object', () => {
    const displayWindow = openDisplayWindow();
    
    // 戻り値がオブジェクトであることを確認
    expect(displayWindow).toBeDefined();
    expect(typeof displayWindow).toBe('object');
    
    // postMessageメソッドを持っていることを確認
    expect(displayWindow.postMessage).toBeDefined();
    expect(typeof displayWindow.postMessage).toBe('function');
  });

  test('sends state updates to display window', () => {
    const displayWindow = {
      postMessage: jest.fn()
    };
    
    const state = {
      isPlaying: true,
      mouthOpenValue: 0.8
    };
    
    sendStateToDisplayWindow(displayWindow, state);
    
    expect(displayWindow.postMessage).toHaveBeenCalledWith({
      type: 'STATE_UPDATE',
      payload: state
    }, '*');
  });

  test('handles null display window gracefully', () => {
    expect(() => {
      sendStateToDisplayWindow(null, { isPlaying: true });
    }).not.toThrow();
  });
}); 