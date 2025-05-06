# usapyon

## プロジェクト概要

usapyonは、Discordのボイスチャットでテキストメッセージをリアルタイムに音声合成して読み上げるためのBotです。VOICEVOXエンジンと連携し、様々なキャラクターの声でメッセージを読み上げることができます。

## 主な機能

- テキストメッセージの音声合成読み上げ: ボイスチャンネルに参加しているユーザーのテキストメッセージを音声合成して再生します。
- 多チャンネル対応: 複数のボイスチャンネルで同時に利用可能です。
- 話者設定: ユーザーごと、またはサーバー全体で読み上げに使用するVOICEVOXのキャラクター（話者）を設定できます。
- 読み上げ辞書登録: 特定の単語やフレーズの読み方をカスタマイズできます。
- コマンドによる操作:
    - Botをボイスチャンネルに参加させる (`!join`): ユーザーが参加しているボイスチャンネルにBotを参加させます。最後にjoinコマンドが実行されたテキストチャンネルのメッセージを読み上げ対象とします。
    - Botをボイスチャンネルから退出させる (`!leave`): Botをボイスチャンネルから退出させます。
    - 現在読み上げ中のメッセージをスキップする (`!skip`): 現在再生中の音声を停止し、キューに次の音声があれば再生します。再生キューが空で音声合成キューにリクエストがある場合は、現在の音声合成をキャンセルします。
    - 現在の再生を停止し、再生キューと音声合成キューを空にする (`!clear`)

## セットアップ

### Rust環境設定

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
