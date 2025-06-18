/**
 * バックエンドAPIとの通信を行うサービス
 */

/**
 * 漫才スクリプトを生成する
 * @param {string} topic 漫才のトピック
 * @param {boolean} [useMock=false] モックデータを使用するかどうか
 * @returns {Promise<Object>} 生成されたスクリプトとオーディオデータ
 */
export const generateManzaiScript = async (topic, useMock = false) => {
  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topic,
        use_mock: useMock  // 明示的にモック使用有無を指定
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error generating manzai script:', error);
    throw error;
  }
};

/**
 * 話者一覧を取得する
 * @returns {Promise<Array>} VoiceVoxの話者一覧
 */
export const getSpeakers = async () => {
  try {
    const response = await fetch('/api/speakers');

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data.speakers || [];
  } catch (error) {
    console.error('Error fetching speakers:', error);
    throw error;
  }
};

/**
 * ヘルスチェックを行う
 * @returns {Promise<Object>} APIの状態
 */
export const checkHealth = async () => {
  try {
    const response = await fetch('/api/health');

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

/**
 * タイミングデータを取得する
 * この関数はバックエンドにエンドポイントがある場合に使用
 * @param {string} text テキスト
 * @param {number} speakerId 話者ID
 * @returns {Promise<Object>} タイミングデータ
 */
export const getTimingData = async (text, speakerId = 1) => {
  try {
    const response = await fetch('/api/timing', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, speaker_id: speakerId }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching timing data:', error);

    // エラー時はモックデータを返す（開発用）
    return {
      accent_phrases: [
        {
          moras: [
            { text: "こ", start_time: 0, end_time: 150 },
            { text: "ん", start_time: 150, end_time: 300 },
            { text: "に", start_time: 300, end_time: 450 },
            { text: "ち", start_time: 450, end_time: 600 },
            { text: "は", start_time: 600, end_time: 750 }
          ]
        }
      ]
    };
  }
};
