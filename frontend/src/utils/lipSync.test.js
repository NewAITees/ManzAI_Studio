import { calculateMouthOpenness } from './lipSync';

describe('lipSync', () => {
  const mockTimingData = {
    accent_phrases: [{
      moras: [
        { text: "こ", start_time: 100, end_time: 150 },
        { text: "ん", start_time: 150, end_time: 200 }
      ]
    }]
  };

  test('calculates correct mouth openness at a given time', () => {
    // 口が開いている時間帯
    expect(calculateMouthOpenness(mockTimingData, 120)).toBeGreaterThan(0);

    // モーラとモーラの間（小さな値になるはず）
    expect(calculateMouthOpenness(mockTimingData, 150)).toBeLessThan(0.5);

    // どのモーラにも該当しない時間帯
    expect(calculateMouthOpenness(mockTimingData, 300)).toBe(0);
  });

  test('handles empty timing data', () => {
    expect(calculateMouthOpenness({}, 100)).toBe(0);
    expect(calculateMouthOpenness({ accent_phrases: [] }, 100)).toBe(0);
  });

  test('handles different mora types', () => {
    const timingData = {
      accent_phrases: [{
        moras: [
          { text: "あ", start_time: 0, end_time: 50 },    // 母音
          { text: "か", start_time: 50, end_time: 100 },  // 子音+母音
          { text: "ん", start_time: 100, end_time: 150 }, // 撥音
          { text: "っ", start_time: 150, end_time: 200 }  // 促音
        ]
      }]
    };

    // 母音は大きく開く
    expect(calculateMouthOpenness(timingData, 25)).toBeGreaterThan(0.7);

    // 子音+母音は中程度
    expect(calculateMouthOpenness(timingData, 75)).toBeLessThan(0.7);
    expect(calculateMouthOpenness(timingData, 75)).toBeGreaterThan(0.3);

    // 撥音は小さく開く
    expect(calculateMouthOpenness(timingData, 125)).toBeLessThan(0.3);
    expect(calculateMouthOpenness(timingData, 125)).toBeGreaterThan(0);

    // 促音はほとんど開かない
    expect(calculateMouthOpenness(timingData, 175)).toBeLessThan(0.2);
  });

  test('interpolates between moras', () => {
    const timingData = {
      accent_phrases: [{
        moras: [
          { text: "あ", start_time: 0, end_time: 50 },
          { text: "い", start_time: 50, end_time: 100 }
        ]
      }]
    };

    // モーラの中間点での補間
    const middleValue = calculateMouthOpenness(timingData, 50);
    const beforeValue = calculateMouthOpenness(timingData, 45);
    const afterValue = calculateMouthOpenness(timingData, 55);

    expect(middleValue).toBeLessThan(beforeValue);
    expect(middleValue).toBeLessThan(afterValue);
  });
});
