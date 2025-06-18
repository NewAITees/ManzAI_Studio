import React from 'react';
import PropTypes from 'prop-types';
import Live2DDisplay from './Live2DDisplay';

const DisplayWindow = ({
  isDisplayMode,
  modelPath,
  isPlaying = false,
  mouthOpenValue = 0,
  onOpenDisplayWindow
}) => {
  return (
    <div className="display-window">
      <Live2DDisplay
        modelPath={modelPath}
        isPlaying={isPlaying}
        mouthOpenValue={mouthOpenValue}
      />

      {!isDisplayMode && (
        <div className="display-controls" data-testid="display-controls">
          <button
            onClick={onOpenDisplayWindow}
            className="open-display-button"
          >
            表示ウィンドウを開く
          </button>
        </div>
      )}
    </div>
  );
};

DisplayWindow.propTypes = {
  isDisplayMode: PropTypes.bool.isRequired,
  modelPath: PropTypes.string.isRequired,
  isPlaying: PropTypes.bool,
  mouthOpenValue: PropTypes.number,
  onOpenDisplayWindow: PropTypes.func
};

export default DisplayWindow;
