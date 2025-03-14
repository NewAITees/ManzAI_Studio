import { render, screen } from '@testing-library/react';
import Live2DDisplay from './Live2DDisplay';
import { loadModel, setParameter } from '../utils/live2d';

// Live2Dモックの設定
jest.mock('../utils/live2d', () => ({
  loadModel: jest.fn(),
  setParameter: jest.fn()
}));

describe('Live2DDisplay', () => {
  beforeEach(() => {
    // 各テストの前にモックをリセット
    jest.clearAllMocks();
  });

  test('loads Live2D model on component mount', () => {
    render(<Live2DDisplay modelPath="test-model.model3.json" />);
    expect(loadModel).toHaveBeenCalledWith("test-model.model3.json");
  });

  test('updates mouth parameter when playing audio', () => {
    render(
      <Live2DDisplay 
        modelPath="test-model.model3.json"
        isPlaying={true} 
        mouthOpenValue={0.8}
      />
    );
    
    expect(setParameter).toHaveBeenCalledWith("ParamMouthOpenY", 0.8);
  });

  test('renders canvas element', () => {
    render(<Live2DDisplay modelPath="test-model.model3.json" />);
    const canvas = screen.getByTestId('live2d-canvas');
    expect(canvas).toBeInTheDocument();
    expect(canvas.tagName).toBe('CANVAS');
  });

  test('does not update mouth parameter when not playing', () => {
    render(
      <Live2DDisplay 
        modelPath="test-model.model3.json"
        isPlaying={false} 
        mouthOpenValue={0.8}
      />
    );
    
    expect(setParameter).not.toHaveBeenCalled();
  });
}); 