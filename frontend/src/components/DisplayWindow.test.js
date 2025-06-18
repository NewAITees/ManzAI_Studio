import { render, screen } from '@testing-library/react';
import DisplayWindow from './DisplayWindow';
import { loadModel, setParameter } from '../utils/live2d';

// Live2Dモックの設定
jest.mock('../utils/live2d', () => ({
  loadModel: jest.fn(),
  setParameter: jest.fn()
}));

describe('DisplayWindow', () => {
  beforeEach(() => {
    // 各テストの前にモックをリセット
    jest.clearAllMocks();
  });

  test('renders in display mode without controls', () => {
    render(<DisplayWindow isDisplayMode={true} modelPath="test-model.model3.json" />);

    // Live2Dキャンバスが表示されていることを確認
    const canvas = screen.getByTestId('live2d-canvas');
    expect(canvas).toBeInTheDocument();

    // コントロール要素が表示されていないことを確認
    const controls = screen.queryByTestId('display-controls');
    expect(controls).not.toBeInTheDocument();
  });

  test('renders in control mode with controls', () => {
    render(<DisplayWindow isDisplayMode={false} modelPath="test-model.model3.json" />);

    // Live2Dキャンバスが表示されていることを確認
    const canvas = screen.getByTestId('live2d-canvas');
    expect(canvas).toBeInTheDocument();

    // コントロール要素が表示されていることを確認
    const controls = screen.getByTestId('display-controls');
    expect(controls).toBeInTheDocument();
  });

  test('applies chroma key background in display mode', () => {
    render(<DisplayWindow isDisplayMode={true} modelPath="test-model.model3.json" />);

    const canvas = screen.getByTestId('live2d-canvas');
    expect(canvas).toHaveStyle({ backgroundColor: '#00ff00' });
  });

  test('syncs with main window state changes', () => {
    const { rerender } = render(
      <DisplayWindow
        isDisplayMode={true}
        modelPath="test-model.model3.json"
        isPlaying={false}
        mouthOpenValue={0}
      />
    );

    // 初期状態では口が動いていないことを確認
    expect(setParameter).not.toHaveBeenCalled();

    // 再生状態に変更
    rerender(
      <DisplayWindow
        isDisplayMode={true}
        modelPath="test-model.model3.json"
        isPlaying={true}
        mouthOpenValue={0.8}
      />
    );

    // 口が動いていることを確認
    expect(setParameter).toHaveBeenCalledWith("ParamMouthOpenY", 0.8);
  });

  test('loads model on mount', () => {
    render(<DisplayWindow isDisplayMode={true} modelPath="test-model.model3.json" />);
    expect(loadModel).toHaveBeenCalledWith("test-model.model3.json");
  });
});
