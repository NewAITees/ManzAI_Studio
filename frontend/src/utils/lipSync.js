/**
 * 母音の開口度を定義
 */
const VOWEL_OPENNESS = {
  'あ': 1.0,   // 最大開口
  'い': 0.3,   // 狭母音
  'う': 0.3,   // 狭母音
  'え': 0.7,   // 中母音
  'お': 0.7,   // 中母音
};

/**
 * 特殊音素の開口度を定義
 */
const SPECIAL_MORA_OPENNESS = {
  'ん': 0.2,   // 撥音
  'っ': 0.1,   // 促音
  'ー': 0.3,   // 長音
};

/**
 * 子音の開口度調整係数を定義
 */
const CONSONANT_FACTORS = {
  'k': 0.5,  // か行
  's': 0.4,  // さ行
  't': 0.4,  // た行
  'n': 0.6,  // な行
  'h': 0.5,  // は行
  'm': 0.6,  // ま行
  'y': 0.7,  // や行
  'r': 0.6,  // ら行
  'w': 0.7,  // わ行
  'g': 0.5,  // が行
  'z': 0.4,  // ざ行
  'd': 0.4,  // だ行
  'b': 0.5,  // ば行
  'p': 0.5   // ぱ行
};

/**
 * モーラから母音を抽出
 * @param {string} mora モーラ（ひらがな1文字または2文字）
 * @returns {string} 母音
 */
const extractVowel = (mora) => {
  // 特殊音素の場合はそのまま返す
  if (mora in SPECIAL_MORA_OPENNESS) {
    return mora;
  }

  // 母音の場合はそのまま返す
  if (mora in VOWEL_OPENNESS) {
    return mora;
  }

  // 子音+母音の場合は母音を抽出
  const vowelMap = {
    'か': 'あ', 'き': 'い', 'く': 'う', 'け': 'え', 'こ': 'お',
    'さ': 'あ', 'し': 'い', 'す': 'う', 'せ': 'え', 'そ': 'お',
    'た': 'あ', 'ち': 'い', 'つ': 'う', 'て': 'え', 'と': 'お',
    'な': 'あ', 'に': 'い', 'ぬ': 'う', 'ね': 'え', 'の': 'お',
    'は': 'あ', 'ひ': 'い', 'ふ': 'う', 'へ': 'え', 'ほ': 'お',
    'ま': 'あ', 'み': 'い', 'む': 'う', 'め': 'え', 'も': 'お',
    'や': 'あ', 'ゆ': 'う', 'よ': 'お',
    'ら': 'あ', 'り': 'い', 'る': 'う', 'れ': 'え', 'ろ': 'お',
    'わ': 'あ', 'を': 'お',
    'が': 'あ', 'ぎ': 'い', 'ぐ': 'う', 'げ': 'え', 'ご': 'お',
    'ざ': 'あ', 'じ': 'い', 'ず': 'う', 'ぜ': 'え', 'ぞ': 'お',
    'だ': 'あ', 'ぢ': 'い', 'づ': 'う', 'で': 'え', 'ど': 'お',
    'ば': 'あ', 'び': 'い', 'ぶ': 'う', 'べ': 'え', 'ぼ': 'お',
    'ぱ': 'あ', 'ぴ': 'い', 'ぷ': 'う', 'ぺ': 'え', 'ぽ': 'お'
  };

  return vowelMap[mora] || 'あ';  // デフォルトは'あ'
};

/**
 * モーラの子音を判定
 * @param {string} mora モーラ（ひらがな1文字または2文字）
 * @returns {string|null} 子音の種類（k, s, t, など）またはnull
 */
const getConsonantType = (mora) => {
  const consonantMap = {
    'か': 'k', 'き': 'k', 'く': 'k', 'け': 'k', 'こ': 'k',
    'さ': 's', 'し': 's', 'す': 's', 'せ': 's', 'そ': 's',
    'た': 't', 'ち': 't', 'つ': 't', 'て': 't', 'と': 't',
    'な': 'n', 'に': 'n', 'ぬ': 'n', 'ね': 'n', 'の': 'n',
    'は': 'h', 'ひ': 'h', 'ふ': 'h', 'へ': 'h', 'ほ': 'h',
    'ま': 'm', 'み': 'm', 'む': 'm', 'め': 'm', 'も': 'm',
    'や': 'y', 'ゆ': 'y', 'よ': 'y',
    'ら': 'r', 'り': 'r', 'る': 'r', 'れ': 'r', 'ろ': 'r',
    'わ': 'w', 'を': 'w',
    'が': 'g', 'ぎ': 'g', 'ぐ': 'g', 'げ': 'g', 'ご': 'g',
    'ざ': 'z', 'じ': 'z', 'ず': 'z', 'ぜ': 'z', 'ぞ': 'z',
    'だ': 'd', 'ぢ': 'd', 'づ': 'd', 'で': 'd', 'ど': 'd',
    'ば': 'b', 'び': 'b', 'ぶ': 'b', 'べ': 'b', 'ぼ': 'b',
    'ぱ': 'p', 'ぴ': 'p', 'ぷ': 'p', 'ぺ': 'p', 'ぽ': 'p'
  };

  return consonantMap[mora] || null;
};

/**
 * モーラの開口度を計算
 * @param {string} mora モーラ（ひらがな1文字または2文字）
 * @returns {number} 開口度（0-1）
 */
const calculateMoraOpenness = (mora) => {
  // 特殊音素の場合
  if (mora in SPECIAL_MORA_OPENNESS) {
    return SPECIAL_MORA_OPENNESS[mora];
  }

  // 母音を抽出
  const vowel = extractVowel(mora);
  const baseOpenness = VOWEL_OPENNESS[vowel] || 0.5;

  // 子音+母音の場合は開口度を調整
  const consonantType = getConsonantType(mora);
  if (consonantType) {
    const factor = CONSONANT_FACTORS[consonantType] || 0.5;
    return baseOpenness * factor;
  }

  return baseOpenness;
};

/**
 * 指定された時間における口の開き具合を計算
 * @param {Object} timingData VoiceVoxから取得したタイミングデータ
 * @param {number} currentTime 現在の時間（ミリ秒）
 * @returns {number} 口の開き具合（0-1）
 */
export const calculateMouthOpenness = (timingData, currentTime) => {
  // タイミングデータが不正な場合は0を返す
  if (!timingData.accent_phrases || !Array.isArray(timingData.accent_phrases)) {
    return 0;
  }

  // 現在の時間に該当するモーラを探す
  for (const phrase of timingData.accent_phrases) {
    if (!phrase.moras || !Array.isArray(phrase.moras)) {
      continue;
    }

    for (let i = 0; i < phrase.moras.length; i++) {
      const mora = phrase.moras[i];

      if (currentTime >= mora.start_time && currentTime <= mora.end_time) {
        const openness = calculateMoraOpenness(mora.text);

        // モーラ内での位置に基づいて補間（山なりの曲線）
        const position = (currentTime - mora.start_time) / (mora.end_time - mora.start_time);
        return openness * Math.sin(position * Math.PI);
      }

      // モーラとモーラの間の補間
      if (i < phrase.moras.length - 1) {
        const nextMora = phrase.moras[i + 1];
        if (currentTime > mora.end_time && currentTime < nextMora.start_time) {
          const openness1 = calculateMoraOpenness(mora.text);
          const openness2 = calculateMoraOpenness(nextMora.text);

          // 線形補間
          const t = (currentTime - mora.end_time) / (nextMora.start_time - mora.end_time);
          return openness1 * (1 - t) + openness2 * t;
        }
      }
    }
  }

  return 0;  // 該当する時間が見つからない場合は0
};
