import React, { useState } from 'react';
import PropTypes from 'prop-types';

const InputForm = ({ onSubmit, isGenerating = false }) => {
  const [topic, setTopic] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!topic.trim()) {
      setError('トピックを入力してください');
      return;
    }

    setError('');
    onSubmit(topic);
  };

  return (
    <form onSubmit={handleSubmit} className="input-form">
      <div className="form-group">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="トピックを入力"
          disabled={isGenerating}
          className="form-control"
        />
        {error && <div className="error-message">{error}</div>}
      </div>
      <button
        type="submit"
        disabled={isGenerating}
        className="submit-button"
      >
        {isGenerating ? '生成中...' : '生成'}
      </button>
    </form>
  );
};

InputForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isGenerating: PropTypes.bool
};

export default InputForm;
