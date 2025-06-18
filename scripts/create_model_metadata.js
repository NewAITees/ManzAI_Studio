/**
 * Live2Dモデル用のメタデータファイル作成スクリプト
 *
 * 使用方法:
 *   node scripts/create_model_metadata.js
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// モデルディレクトリパス
const MODELS_DIR = path.join(__dirname, '..', 'frontend', 'public', 'live2d', 'models');

// モデルの種類
const MODEL_TYPES = ['tsukkomi', 'boke', 'unknown'];

// プロンプト関数
const prompt = (question) => {
  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      resolve(answer);
    });
  });
};

// メインプロセス
const main = async () => {
  try {
    console.log('Live2Dモデルメタデータ作成ツール');
    console.log('=================================');

    // モデルディレクトリの存在確認
    if (!fs.existsSync(MODELS_DIR)) {
      console.error(`モデルディレクトリが見つかりません: ${MODELS_DIR}`);
      return;
    }

    // モデルディレクトリ一覧を取得
    const modelDirs = fs.readdirSync(MODELS_DIR, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory())
      .map(dirent => dirent.name);

    if (modelDirs.length === 0) {
      console.log('モデルディレクトリが見つかりません。');
      return;
    }

    console.log('利用可能なモデルディレクトリ:');
    modelDirs.forEach((dir, index) => {
      console.log(`  ${index + 1}. ${dir}`);
    });

    // モデルの選択
    const modelIndexStr = await prompt('処理するモデルの番号を入力してください: ');
    const modelIndex = parseInt(modelIndexStr, 10) - 1;

    if (isNaN(modelIndex) || modelIndex < 0 || modelIndex >= modelDirs.length) {
      console.error('無効な番号です。');
      return;
    }

    const modelDir = modelDirs[modelIndex];
    const modelPath = path.join(MODELS_DIR, modelDir);

    console.log(`\n"${modelDir}" のメタデータを作成します。`);

    // model3.jsonファイルを検索
    const modelFiles = fs.readdirSync(modelPath)
      .filter(file => file.endsWith('.model3.json'));

    if (modelFiles.length === 0) {
      console.error('model3.jsonファイルが見つかりません。');
      return;
    }

    // model3.jsonファイルの選択
    let modelFile;
    if (modelFiles.length === 1) {
      modelFile = modelFiles[0];
      console.log(`モデルファイル: ${modelFile}`);
    } else {
      console.log('利用可能なモデルファイル:');
      modelFiles.forEach((file, index) => {
        console.log(`  ${index + 1}. ${file}`);
      });

      const fileIndexStr = await prompt('使用するモデルファイルの番号を入力してください: ');
      const fileIndex = parseInt(fileIndexStr, 10) - 1;

      if (isNaN(fileIndex) || fileIndex < 0 || fileIndex >= modelFiles.length) {
        console.error('無効な番号です。');
        return;
      }

      modelFile = modelFiles[fileIndex];
    }

    // テクスチャファイルを検索
    const textureFiles = fs.readdirSync(modelPath)
      .filter(file => file.endsWith('.png') || file.endsWith('.jpg') || file.endsWith('.jpeg'));

    // メタデータの入力
    const name = await prompt('モデル名を入力してください: ');

    console.log('\nモデルの種類:');
    MODEL_TYPES.forEach((type, index) => {
      console.log(`  ${index + 1}. ${type}`);
    });

    const typeIndexStr = await prompt('モデルの種類の番号を入力してください: ');
    const typeIndex = parseInt(typeIndexStr, 10) - 1;

    if (isNaN(typeIndex) || typeIndex < 0 || typeIndex >= MODEL_TYPES.length) {
      console.error('無効な番号です。');
      return;
    }

    const type = MODEL_TYPES[typeIndex];

    // メタデータの作成
    const metadata = {
      name,
      type,
      model: modelFile,
      textures: textureFiles,
      version: "1.0.0"
    };

    // メタデータの保存
    const metadataPath = path.join(modelPath, 'model.json');
    fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2), 'utf8');

    console.log(`\nメタデータが作成されました: ${metadataPath}`);

    // サムネイル確認
    const thumbnailPath = path.join(modelPath, 'thumbnail.png');
    if (!fs.existsSync(thumbnailPath)) {
      console.log('\n警告: サムネイル画像 (thumbnail.png) が見つかりません。');
      console.log('サムネイル画像を追加すると、モデル選択画面でモデルを視覚的に識別できます。');
    }
  } catch (error) {
    console.error('エラーが発生しました:', error);
  } finally {
    rl.close();
  }
};

main();
