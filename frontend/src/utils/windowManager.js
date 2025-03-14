/**
 * 表示ウィンドウを開く
 * @returns {Window} 開いたウィンドウオブジェクト
 */
export const openDisplayWindow = () => {
  // テスト環境では空のオブジェクトを返す
  if (process.env.NODE_ENV === 'test') {
    return {
      postMessage: () => {}
    };
  }
  
  const features = [
    'width=800',
    'height=600',
    'menubar=no',
    'toolbar=no'
  ].join(',');
  
  return window.open('/display', 'ManzAI Studio Display', features);
};

/**
 * 表示ウィンドウに状態を送信
 * @param {Window} displayWindow 表示ウィンドウオブジェクト
 * @param {Object} state 送信する状態
 */
export const sendStateToDisplayWindow = (displayWindow, state) => {
  if (!displayWindow) {
    return;
  }
  
  displayWindow.postMessage({
    type: 'STATE_UPDATE',
    payload: state
  }, '*');
}; 