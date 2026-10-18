# 2026_ML_DS ML-HW02：コマンドで提出する場合

通常はREADMEのGitHub Desktopの手順で提出できます。`gh student` は任意の追加ツールです。この課題は `main` へのpushで提出されるため、Gitのcommitとpushでも提出できます。

## 通常のGitで提出する

課題を受け取り、自分のリポジトリをcloneしたフォルダで実行します。先に `git status` と `git remote -v` で、作業場所と提出先を確認してください。

```shell
git add ml02_1.py ml02_2.py
git commit -m "Complete ML-HW02 exercises"
git pull --rebase
git push origin main
```

競合が出た場合は、自分のコードを残して教員またはTAに相談してください。強制pushは使いません。提出後はGitHubのActionsで基本確認の結果を確認します。

## `gh student` を使う場合

Gitと[GitHub CLI](https://cli.github.com/)を使える環境で、[公式の学生用拡張機能](https://github.com/foundation50/gh-student)を追加します。`gh` だけをインストールしても、`gh student` は使えません。

未導入の場合は、次のコマンドを1回実行します。

```shell
gh extension install foundation50/gh-student
```

導入済みの場合は、次のコマンドで更新できます。

```shell
gh extension upgrade gh-student
```

```shell
gh student --version
gh student login
```

Classroom 50と同じGitHubアカウントでログインします。2026年10月8日時点の公式リリースはv1.57.0です。

自分の課題リポジトリのフォルダで、教員からの更新を先に取り込みます。GitHub DesktopならFetch origin、更新があればPull originを押します。未commitの変更がある場合は先に自分の変更をcommitしてください。

```shell
git status
git remote -v
gh student submit
```

`gh student submit` は、追跡中のファイルと `.gitignore` で除外されていないファイルをまとめてcommitしてpushします。実行前に、提出対象外のファイルが含まれていないことを確認してください。

この課題では独自の基本確認を使っています。`.classroom50.yaml` がなくても、対応する学生CLIはリポジトリ名と公開された課題情報から提出先を調べます。ファイルを自分で追加したり、採点設定を変更したりする必要はありません。

## うまく動かない場合

| 表示・状態 | 確認すること |
|---|---|
| `gh` が見つからない | GitHub CLIをインストール後、ターミナルを開き直す |
| `student` が不明なコマンド | 学生用拡張機能を導入し、`gh student --version` を確認する |
| 認証・権限のエラー | `gh student login` で課題を受け取ったアカウントにログインし、Organizationへの参加と自分のリポジトリへのアクセスを確認する |
| `.classroom50.yaml` や課題情報のエラー | 拡張機能を更新し、自分の課題リポジトリ内で実行しているか、`origin` が正しいかを確認する |
| `git pull` を求められる | 教員からの更新を取り込んでから再実行する。競合が出たら強制pushせず相談する |

解決しない場合は、エラー全文と `gh student --version` の結果を教員またはTAに伝えてください。パスワードやアクセストークンは送らないでください。GitHub Desktopまたは通常のGitでpushできれば、この課題の提出は可能です。

## 結果の確認

GitHubの **Actions → ML-HW02 Basic checks** を開きます。この課題ではファイルの提出形式だけを確認し、答案のコードは実行しません。緑のチェックでも正解や満点を意味しません。正式な採点は締切後に教員が別途行い、この画面には点数を表示しません。
