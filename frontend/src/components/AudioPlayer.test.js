import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AudioPlayer from './AudioPlayer';

// Audio要素のモック
window.HTMLMediaElement.prototype.play = jest.fn();
window.HTMLMediaElement.prototype.pause = jest.fn();
window.HTMLMediaElement.prototype.load = jest.fn();

describe('AudioPlayer', () => {
  const mockAudioData = [
    { role: 'tsukkomi', audio_path: '/audio/1.wav' },
    { role: 'boke', audio_path: '/audio/2.wav' }
  ];

  beforeEach(() => {
    // 各テストの前にモックをリセット
    jest.clearAllMocks();
  });

  test('renders play button when not playing', () => {
    render(<AudioPlayer audioData={mockAudioData} onPlayStateChange={() => {}} />);
    const playButton = screen.getByRole('button', { name: /再生/i });
    expect(playButton).toBeInTheDocument();
  });

  test('changes to pause button when playing', async () => {
    render(<AudioPlayer audioData={mockAudioData} onPlayStateChange={() => {}} />);

    const playButton = screen.getByRole('button', { name: /再生/i });
    await act(async () => {
      await userEvent.click(playButton);
    });

    const pauseButton = screen.getByRole('button', { name: /停止/i });
    expect(pauseButton).toBeInTheDocument();
  });

  test('calls onPlayStateChange when play state changes', async () => {
    const handlePlayStateChange = jest.fn();
    render(<AudioPlayer audioData={mockAudioData} onPlayStateChange={handlePlayStateChange} />);

    const playButton = screen.getByRole('button', { name: /再生/i });
    await act(async () => {
      await userEvent.click(playButton);
    });

    expect(handlePlayStateChange).toHaveBeenCalledWith(true);

    const pauseButton = screen.getByRole('button', { name: /停止/i });
    await act(async () => {
      await userEvent.click(pauseButton);
    });

    expect(handlePlayStateChange).toHaveBeenCalledWith(false);
  });

  test('loads audio files when provided', () => {
    render(<AudioPlayer audioData={mockAudioData} onPlayStateChange={() => {}} />);

    const audioElements = screen.getAllByTestId('audio-element');
    expect(audioElements).toHaveLength(mockAudioData.length);

    audioElements.forEach((audio, index) => {
      expect(audio).toHaveAttribute('src', mockAudioData[index].audio_path);
    });
  });

  test('handles empty audio data', () => {
    render(<AudioPlayer audioData={[]} onPlayStateChange={() => {}} />);

    const playButton = screen.getByRole('button', { name: /再生/i });
    expect(playButton).toBeDisabled();
  });
});
