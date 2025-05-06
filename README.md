# usapyon - Discordボイスチャット読み上げBot

## 📖 はじめに

usapyonは、Discordのボイスチャットでテキストメッセージをリアルタイムに音声合成して読み上げるためのBotです。
VOICEVOXエンジンと連携し、様々なキャラクターの声でメッセージを楽しく読み上げます。

## ✨ 主な機能

-   **リアルタイム読み上げ**: ボイスチャンネルに参加しているユーザーのテキストメッセージを音声合成して再生します。
-   **多チャンネル対応**: 複数のボイスチャンネルで同時に利用できます。
-   **声のカスタマイズ**:
    -   ユーザーごとに、またはサーバー全体で読み上げに使用するVOICEVOXのキャラクター（話者）を設定できます。
    -   特定の単語やフレーズの読み方をカスタマイズできる辞書機能があります。
-   **かんたん操作**: シンプルなコマンドでBotを操作できます。
    -   `!join`: Botをボイスチャンネルに参加させます。
    -   `!leave`: Botをボイスチャンネルから退出させます。
    -   `!skip`: 現在読み上げ中のメッセージをスキップします。
    -   `!clear`: 再生中の音声を停止し、キューを空にします。

## 🚀 セットアップ

usapyonを動かすために必要な準備をステップごとに説明します。

### 1. Rust環境の準備

usapyonはRustというプログラミング言語で作られています。まず、Rustをインストールしましょう。

-   **Rustのインストール**:
    -   [Rust公式サイトの手順](https://www.rust-lang.org/tools/install)に従ってインストールしてください。
-   **必要なライブラリのインストール (Linuxの場合)**:
    ターミナルで以下のコマンドを実行します。
    ```bash
    sudo apt-get update
    sudo apt-get install pkg-config libssl-dev cmake
    ```

### 2. Discord Botの準備

次に、Discordでusapyonとして動作するBotアカウントを作成し、設定します。

-   **Botアカウントの作成**:
    1.  [Discord Developer Portal](https://discord.com/developers/applications)にアクセスし、ログインします。
    2.  「New Application」ボタンを押し、Botの名前（例: usapyon）を入力して作成します。
    3.  左側のメニューから「Bot」を選び、「Add Bot」をクリックします。
-   **トークンの取得**:
    -   Botページの「TOKEN」セクションにある「Reset Token」または「Copy Token」ボタンでトークンを取得し、安全な場所に控えておいてください。**このトークンは他人に教えないでください。**
-   **必要な権限の有効化 (Privileged Gateway Intents)**:
    Botページで以下の設定を有効にしてください。
    -   `PRESENCE INTENT`
    -   `SERVER MEMBERS INTENT`
    -   `MESSAGE CONTENT INTENT`
-   **Botをサーバーに追加**:
    1.  左側のメニューから「OAuth2」を選び、その中の「URL Generator」を開きます。
    2.  「SCOPES」で以下を選択します。
        -   `bot`
        -   `applications.commands`
    3.  「BOT PERMISSIONS」でBotに必要な権限を選択します（例: `Send Messages`, `Connect`, `Speak`など、読み上げに必要な権限）。
    4.  生成されたURLをコピーし、ブラウザで開きます。
    5.  Botを追加したいサーバーを選択し、認証します（サーバーの管理者権限が必要です）。

### 3. VOICEVOXエンジンの準備 (Linux CPU版)

usapyonが声を出すためには、VOICEVOXエンジンが必要です。

-   **エンジンのダウンロード**:
    1.  [VOICEVOXエンジンのリリースページ](https://github.com/VOICEVOX/voicevox_engine/releases)にアクセスします。
    2.  最新リリースの「Assets」の中から、`voicevox_engine-linux-cpu-X.X.X.7z.001` (X.X.Xはバージョン番号) のような名前のファイルをダウンロードします。リンクを右クリックして「名前を付けてリンク先を保存」などで保存してください。
        ```bash
        # 例 (バージョンは適宜最新のものに置き換えてください)
        wget https://github.com/VOICEVOX/voicevox_engine/releases/download/0.18.1/voicevox_engine-linux-cpu-0.18.1.7z.001
        ```
-   **7-Zipのインストール (解凍用)**:
    ダウンロードしたファイルは7z形式なので、解凍ツールをインストールします。
    ```bash
    sudo apt install p7zip-full
    ```
-   **エンジンの解凍と配置**:
    ダウンロードしたファイルを解凍し、ホームディレクトリ直下に `voicevox_engine` という名前で配置します。
    ターミナルで、ダウンロードしたファイルがあるディレクトリに移動し、以下のコマンドを実行します。
    ```bash
    # 'voicevox_engine-linux-cpu-X.X.X.7z.001' の部分はダウンロードしたファイル名に置き換えてください
    7z x voicevox_engine-linux-cpu-0.18.1.7z.001 -o$HOME/voicevox_engine
    ```
    *(注意: `-o`オプションとパス `$HOME/voicevox_engine` の間にスペースはありません)*
-   **エンジンの起動確認 (任意)**:
    正しく配置できたか確認するため、エンジンを一度起動してみましょう。
    ```bash
    $HOME/voicevox_engine/linux-cpu/run
    ```
    起動メッセージが表示されればOKです。確認後は `Ctrl+C` で終了してください。

### 4. Botの設定ファイル作成

BotがDiscordに接続するための情報を設定ファイルに記述します。

1.  プロジェクトのルートディレクトリ（この`README.md`がある場所）に `.env` という名前のファイルを作成します。
2.  `.env`ファイルに以下のようにDiscord Botのトークンを記述します。
    ```env
    DISCORD_TOKEN=[ここに取得したDiscord Botのトークンを貼り付け]
    ```

### 5. Botの起動

全ての準備が整ったら、いよいよBotを起動します。

1.  ターミナルでこのプロジェクトのディレクトリに移動します。
2.  以下のコマンドを実行してBotを起動します。
    ```bash
    cargo run --release
    ```
    初回起動時はビルドに時間がかかることがあります。

## 🛠️ 使い方 (コマンド一覧)

Botがボイスチャンネルに参加している状態で、テキストチャンネルに以下のコマンドを入力することで操作できます。

-   `!join`
    -   **機能**: あなたが現在参加しているボイスチャンネルにBotを参加させます。
    -   **備考**: このコマンドが最後に実行されたテキストチャンネルのメッセージが読み上げ対象になります。
-   `!leave`
    -   **機能**: Botをボイスチャンネルから退出させます。
-   `!skip`
    -   **機能**: 現在再生中の音声を停止し、キューに次の音声があれば再生します。
    -   **備考**: 再生キューが空で、まだ音声合成が完了していないリクエストがある場合、その音声合成をキャンセルします。
-   `!clear`
    -   **機能**: 現在の再生を停止し、再生キューと音声合成キューの両方を空にします。

## 🔧 応用設定 (予定)

-   話者設定 (ユーザーごと、サーバー全体)
-   読み上げ辞書登録

## 困ったときは (トラブルシューティング)

(今後、よくある質問や問題点を追記予定です)

## ❤️ 貢献

(バグ報告や機能提案など、歓迎します！ IssueやPull Requestでお知らせください。)
