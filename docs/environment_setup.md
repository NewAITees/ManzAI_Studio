# 環境構築ガイド

このドキュメントでは、ManzAI Studioの開発環境のセットアップ方法について説明します。特にM1/M2 Mac環境での問題解決に焦点を当てています。

## 目次

1. [前提条件](#前提条件)
2. [基本的なセットアップ](#基本的なセットアップ)
3. [M1/M2 Mac固有の問題解決](#m1m2-mac固有の問題解決)
4. [Poetry環境の設定](#poetry環境の設定)
5. [トラブルシューティング](#トラブルシューティング)

## 前提条件

- macOS 11.0以降
- Homebrew
- Command Line Tools for Xcode

## 基本的なセットアップ

### 1. 必要な依存関係のインストール

```bash
# 基本的な依存関係
brew install openssl readline sqlite3 xz zlib tcl-tk

# gettext（ロケール関連の依存関係）
brew install gettext

# Rosetta 2のインストール（必要な場合）
softwareupdate --install-rosetta
```

### 2. pyenvのインストール（オプション）

```bash
brew install pyenv
```

## M1/M2 Mac固有の問題解決

### 環境変数の設定

`.zshrc`または`.bash_profile`に以下を追加します：

```bash
# Python関連の環境変数
export LDFLAGS="-L/usr/local/opt/gettext/lib"
export CPPFLAGS="-I/usr/local/opt/gettext/include"
export PYTHON_CONFIGURE_OPTS="--enable-framework"

# pyenvを使用する場合の追加設定
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"

# M1 Mac用のPython構築設定
export PYTHON_CONFIGURE_OPTS="--enable-framework --with-tcltk-includes='-I/opt/homebrew/opt/tcl-tk/include' --with-tcltk-libs='-L/opt/homebrew/opt/tcl-tk/lib -ltcl8.6 -ltk8.6'"
export CFLAGS="-I/opt/homebrew/opt/openssl@1.1/include -I/opt/homebrew/opt/readline/include -I/opt/homebrew/opt/sqlite/include -I/opt/homebrew/opt/xz/include"
export LDFLAGS="-L/opt/homebrew/opt/openssl@1.1/lib -L/opt/homebrew/opt/readline/lib -L/opt/homebrew/opt/sqlite/lib -L/opt/homebrew/opt/xz/lib"
```

### Python 3.10のインストール

pyenvでのインストールに問題が発生する場合は、Homebrewを使用します：

```bash
# HomebrewでPython 3.10をインストール
brew install python@3.10

# パスを通す（必要な場合）
export PATH="/usr/local/opt/python@3.10/libexec/bin:$PATH"
```

## Poetry環境の設定

### 1. Poetryのインストール

```bash
brew install poetry
```

### 2. プロジェクトの設定

```bash
# HomebrewでインストールしたPythonを使用してpoetry環境を作成
poetry env use /usr/local/bin/python3.10

# 依存関係のインストール
poetry install
```

## トラブルシューティング

### pyenvでPythonのインストールに失敗する場合

1. Homebrewを使用してPythonを直接インストールする
2. 必要な依存関係が全てインストールされているか確認
3. 環境変数が正しく設定されているか確認

### Poetry環境の作成に失敗する場合

1. Pythonのパスが正しいか確認
2. Poetry自体を再インストール
3. キャッシュをクリア: `poetry cache clear . --all`

### その他の問題

- ビルドエラーが発生する場合は、XcodeとCommand Line Toolsが最新かチェック
- パス関連の問題は、`.zshrc`または`.bash_profile`の設定を確認
- M1/M2 Mac特有の問題は、Rosetta 2のインストールを確認

## 参考リンク

- [pyenv GitHub](https://github.com/pyenv/pyenv)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Homebrew Documentation](https://docs.brew.sh)
- [Apple Silicon Transition Guide](https://developer.apple.com/documentation/apple-silicon) 