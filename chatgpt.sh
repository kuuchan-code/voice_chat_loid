#!/bin/bash
# 出力ファイルをクリア（既存の内容を削除）
echo "" > cpp_files.md

# カレントディレクトリとサブディレクトリの.cppファイルを検索し、内容を出力
find . -name "*.cpp" -print | while read file; do
    echo "### $file" >> cpp_files.md        # ファイル名を見出しとして追加
    echo '```cpp' >> cpp_files.md           # C++ シンタックスハイライトの開始を追加
    
    # clang-formatを使用してC++ファイルをフォーマット
    clang-format -i "$file"

    cat "$file" >> cpp_files.md             # ファイルの内容を追加
    echo '```' >> cpp_files.md              # シンタックスハイライトの終了を追加
done

echo 'このアプリケーションを100点満点で採点し、特に改善すべき部分を修正したコードを示してください。' >> cpp_files.md
