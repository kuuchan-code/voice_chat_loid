#!/bin/bash
# 出力ファイルをクリア（既存の内容を削除）
echo "" > nodjs_files.md

# カレントディレクトリとサブディレクトリの.jsファイルを検索し、内容を出力
# 'node_modules' ディレクトリは除外
find . -path ./node_modules -prune -o -name "*.js" -print | while read file; do
    echo "### $file" >> nodjs_files.md    # ファイル名を見出しとして追加
    echo '```javascript' >> nodjs_files.md    # JavaScript シンタックスハイライトの開始を追加
    
    # eslintを使用してJavaScriptファイルをフォーマット
    eslint --fix "$file"

    cat "$file" >> nodjs_files.md         # ファイルの内容を追加
    echo '```' >> nodjs_files.md          # シンタックスハイライトの終了を追加
done

echo 'このアプリケーションを100点満点で採点し、特に改善すべき部分を修正したコードを示してください。' >> nodjs_files.md
