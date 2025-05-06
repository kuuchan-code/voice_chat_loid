# VoiceChatLoid

## プロジェクト概要

VoiceChatLoidは、Discordのボイスチャットでテキストメッセージをリアルタイムに音声合成して読み上げるためのBotです。VOICEVOXエンジンと連携し、様々なキャラクターの声でメッセージを読み上げることができます。

## 主な機能

- テキストメッセージの音声合成読み上げ: ボイスチャンネルに参加しているユーザーのテキストメッセージを音声合成して再生します。
- 多チャンネル対応: 複数のボイスチャンネルで同時に利用可能です。
- 話者設定: ユーザーごと、またはサーバー全体で読み上げに使用するVOICEVOXのキャラクター（話者）を設定できます。
- 読み上げ辞書登録: 特定の単語やフレーズの読み方をカスタマイズできます。
- コマンドによる操作:
    - Botをボイスチャンネルに参加させる (`/join`)
    - Botをボイスチャンネルから退出させる (`/leave`)
    - 現在の読み上げ設定情報を表示する (`/info`)
    - 読み上げ設定を変更する (`/settings`)
    - 現在読み上げ中のメッセージをスキップする (`/skip`)
    - ヘルプメッセージを表示する (`/help`)
    - 追加の読み上げ対象チャンネルを設定する (`/add_channel`)

## セットアップ

### Python環境設定

- `sudo apt-get install mecab mecab-ipadic mecab-ipadic-utf8 libmecab-dev`
- `pip install -r requirements.txt`

rust

- [Rustのインストールはこちら](https://www.rust-lang.org/tools/install)
- `sudo apt-get install pkg-config libssl-dev`
- `sudo apt-get install cmake`

### ボットアカウント作成

- [Discord Developer Portal](https://discord.com/developers/applications)にアクセス
- トークン取得
- "PRESENCE INTENT"を有効にする
- "SERVER MEMBERS INTENT"を有効にする
- "MESSAGE CONTENT INTENT"を有効にする

### ボットアカウントにログインする

#### トークン登録
.envファイルを作成し、以下のようにトークンを登録してください。

```:.env
DISCORD_TOKEN=[Discordのトークン]
```

### ボットをサーバーに追加する

#### サーバーに追加するときのロール

OAuth2 URL Generator

SCOPES
- bot
- applications.commands

下にURLが出てくるので、ブラウザにコピペして招待。
自分が管理者になっているサーバーに招待可能。

#### serenityを使う

## voicevox_engineのLinux CPU版をインストール

- [voicevox_engine](https://github.com/VOICEVOX/voicevox_engine)にアクセス。
- リリースページから最新のリリース（エンジン本体）をダウンロード。
- リンクを右クリック、リンク先を保存してください。

例えば現時点では以下のようなURLになります。適宜その時点の最新のリリースページを参照してください。

```bash
$ wget https://github.com/VOICEVOX/voicevox_engine/releases/download/0.18.1/voicevox_engine-linux-cpu-0.18.1.7z.001
```

- 7z形式のファイルを解凍するためにp7zipをインストールします。

```bash
$ sudo apt install p7zip-full
```

- 7z形式のファイルを解凍します。解凍後のファイルはホームディレクトリに配置するように指定します。
ここで、`-o`オプションとパスの間にスペースがないことに注意してください。

```bash
$ 7z x voicevox_engine-linux-cpu-0.18.1.7z.001 -o$HOME/voicevox_engine
```

- `~/voicevox_engine/linux-cpu`ディレクトリができているので、その中の`run`コマンドを実行します。

```bash
$ ~/voicevox_engine/linux-cpu/run
```

<!--
songbirdでwavの再生ができない。
再生できないと思っていたのはDiscordの出力先を間違えていたから。
以下のライブラリが必要か？結論、不要だった。

```bash
sudo apt install libopus-dev
```

以下のライブラリは必須だった。エラーは出ないが再生されない。

```:Cargo.toml
[dependencies.symphonia]
version = "0.5.2"
```
-->
