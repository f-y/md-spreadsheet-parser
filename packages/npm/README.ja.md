# md-spreadsheet-parser (NPM)

<p align="center">
  <img src="https://img.shields.io/badge/wasm-powered-purple.svg" alt="WASM Powered" />
  <a href="https://github.com/f-y/md-spreadsheet-parser/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" />
  </a>
  <a href="https://www.npmjs.com/package/md-spreadsheet-parser">
    <img src="https://img.shields.io/npm/v/md-spreadsheet-parser.svg" alt="npm" />
  </a>
  <a href="https://pypi.org/project/md-spreadsheet-parser/">
    <img src="https://img.shields.io/pypi/v/md-spreadsheet-parser.svg" alt="PyPI" />
  </a>
</p>

**md-spreadsheet-parser** は、Node.js用の堅牢なMarkdownテーブルパーサーおよび操作ライブラリです。
[Pythonコア](https://github.com/f-y/md-spreadsheet-parser) をWebAssemblyにコンパイルして使用しており、Node.jsでネイティブに動作します。

> **🎉 公式GUIエディタが登場: [PengSheets](https://marketplace.visualstudio.com/items?itemName=f-y.peng-sheets)**
>
> このライブラリのパワーをそのままに、VS Code上でExcelライクな操作感を実現しました。ソート、フィルタ、快適なナビゲーションなどをGUIで直感的に扱えます。
>
> [![Get it on VS Code Marketplace](https://img.shields.io/badge/VS%20Code%20Marketplace-%E3%81%A7%E3%83%80%E3%82%A6%E3%83%B3%E3%83%AD%E3%83%BC%E3%83%89-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)](https://marketplace.visualstudio.com/items?itemName=f-y.peng-sheets)

## 機能

- **🚀 高パフォーマンス**: プリコンパイルされたWASMバイナリ（約160msで初期化）。
- **💪 堅牢な解析**: GFMテーブル、列の欠落、エスケープされたパイプを正しく処理します。
- **🛠️ スプレッドシート操作**: セルの編集、行の追加/削除、Markdownの再生成をプログラムで行えます。
- **🛡️ 型安全な検証**: スキーマ（Plain Object または Zod）に対してテーブルデータを検証します。
- **📂 ファイルシステムサポート**: 直接ファイルを読み込む機能を提供します。

## インストール

```bash
npm install md-spreadsheet-parser
```

## 使い方ガイド

### 1. 基本的な解析 (文字列)

Markdownテーブルの文字列を構造化された `Table` オブジェクトに解析します。

```javascript
import { parseTable } from 'md-spreadsheet-parser';

const markdown = `
| Name | Age |
| --- | --- |
| Alice | 30 |
`;

const table = parseTable(markdown);
console.log(table.rows); // [ [ 'Alice', '30' ] ]
```

### 2. ファイルシステムの使用

文字列に読み込むことなく、ファイルを直接解析できます。

```javascript
import { parseWorkbookFromFile, scanTablesFromFile } from 'md-spreadsheet-parser';

// ワークブック全体（複数のシート）を解析
const workbook = parseWorkbookFromFile('./data.md');
console.log(`Parsed ${workbook.sheets.length} sheets`);

// Lookup APIを使用して内容を検証
const sheet = workbook.getSheet('Sheet1');
if (sheet) {
    const table = sheet.getTable(0); // 最初のテーブルを取得
    console.log(table.headers);
}

// または、ファイル内のすべてのテーブルをスキャン
const tables = scanTablesFromFile('./readme.md');
console.log(`Found ${tables.length} tables`);
```

### 3. プログラムによる編集

テーブルオブジェクトは可変です（内部的にはCoWのような動作）。変更してMarkdownにエクスポートし直すことができます。

```javascript
import { parseTable } from 'md-spreadsheet-parser';

const table = parseTable("| Item | Price |\n|---|---|\n| Apple | 100 |");

// セルを更新 (行 0, 列 1)
table.updateCell(0, 1, "150");

// Markdownに戻す
console.log(table.toMarkdown());
// | Item | Price |
// | --- | --- |
// | Apple | 150 |
```

### 4. 型安全な検証 (toModels)

文字列ベースのテーブルデータを、型付きオブジェクトに変換できます。

#### 基本的な使用法 (Plain Object Schema)
コンバータ関数を持つ単純なスキーマオブジェクトを提供できます。

```javascript
const markdown = `
| id | active |
| -- | ------ |
| 1  | yes    |
`;
const table = parseTable(markdown);

// スキーマ定義
const UserSchema = {
    id: (val) => Number(val),
    active: (val) => val === 'yes'
};

const users = table.toModels(UserSchema);
console.log(users);
// [ { id: 1, active: true } ]
```

#### 高度な使用法 (Zod)
より堅牢な検証には、[Zod](https://zod.dev/) を使用してください。

```javascript
import { z } from 'zod';

const UserZodSchema = z.object({
    id: z.coerce.number(),
    active: z.string().transform(v => v === 'yes')
});

const users = table.toModels(UserZodSchema);
// [ { id: 1, active: true } ]
```

## API ドキュメント

このパッケージはPythonコアの直接的なラッパーであるため、基本的な概念は同一です。APIの命名規則はJavaScript用に（snake_caseではなくcamelCaseに）適合されています。

- **コアドキュメント**: [Python ユーザーガイド](https://github.com/f-y/md-spreadsheet-parser/blob/main/README.ja.md#使い方)
- **クックブック**: [一般的なレシピ (日本語)](https://github.com/f-y/md-spreadsheet-parser/blob/main/COOKBOOK.ja.md)

### 主な関数の対応

| Python (Core) | JavaScript (NPM) | 説明 |
|---|---|---|
| `parse_table(md)` | `parseTable(md)` | 単一のテーブル文字列を解析 |
| `parse_workbook(md)` | `parseWorkbook(md)` | ワークブック全体の文字列を解析 |
| `scan_tables(md)` | `scanTables(md)` | 文字列からすべてのテーブルを抽出 |
| `parse_workbook_from_file(path)` | `parseWorkbookFromFile(path)` | ファイルをワークブックに解析 |
| `scan_tables_from_file(path)` | `scanTablesFromFile(path)` | ファイルからテーブルを抽出 |
| `Table.to_markdown()` | `Table.toMarkdown()` | Markdownを生成 |
| `Table.update_cell(r, c, v)` | `Table.updateCell(r, c, v)` | 特定のセルを更新 |
| `Table.to_models(schema)` | `Table.toModels(schema)` | 型付きオブジェクトに変換 |
| `Workbook.get_sheet(name)` | `Workbook.getSheet(name)` | 名前でシートを取得 |
| `Sheet.get_table(index)` | `Sheet.getTable(index)` | インデックスでテーブルを取得 |

## 制限事項

以下のPython機能は、NPMパッケージでは **利用できません**:

| 機能 | 理由 |
|---------|--------|
| `parse_excel()` / `parseExcel()` | Excelファイルの解析には `openpyxl` が必要ですが、これはWASMと互換性がありません |

Excelファイル操作については、[Pythonパッケージ](https://github.com/f-y/md-spreadsheet-parser) を直接使用するか、COOKBOOKにあるようなテキストベース(CSV/TSV)の操作を使ってください。

## アーキテクチャ

このパッケージは、PythonライブラリをWASMコンポーネントとしてバンドルするために `componentize-py` を使用しています。
詳細については、[ARCHITECTURE.md](./ARCHITECTURE.md) を参照してください。

## ライセンス

MIT
