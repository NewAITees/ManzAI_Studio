import { render, screen, fireEvent, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import InputForm from './InputForm';

describe('InputForm', () => {
  test('renders input form with topic field', () => {
    render(<InputForm onSubmit={() => {}} />);
    const inputElement = screen.getByPlaceholderText(/トピックを入力/i);
    expect(inputElement).toBeInTheDocument();
  });

  test('calls onSubmit with topic when form is submitted', async () => {
    const handleSubmit = jest.fn();
    render(<InputForm onSubmit={handleSubmit} />);
    
    const input = screen.getByPlaceholderText(/トピックを入力/i);
    await act(async () => {
      await userEvent.type(input, 'テスト漫才');
    });
    
    const submitButton = screen.getByRole('button', { name: /生成/i });
    await act(async () => {
      await userEvent.click(submitButton);
    });
    
    expect(handleSubmit).toHaveBeenCalledWith('テスト漫才');
  });

  test('shows error when submitting empty topic', async () => {
    render(<InputForm onSubmit={() => {}} />);
    
    const submitButton = screen.getByRole('button', { name: /生成/i });
    await act(async () => {
      await userEvent.click(submitButton);
    });
    
    const errorMessage = screen.getByText(/トピックを入力してください/i);
    expect(errorMessage).toBeInTheDocument();
  });

  test('disables submit button while generating', () => {
    render(<InputForm onSubmit={() => {}} isGenerating={true} />);
    
    const submitButton = screen.getByRole('button', { name: /生成中/i });
    expect(submitButton).toBeDisabled();
  });
}); 