# familiar-ai 基盤強化 — 秘書能力 + 社会性フィードバックループ

## ゴール（ユーザ設定）

> より人間らしく、あるいは社会性高く振る舞えるような基盤にしたい。
> それにあたって、タスク遂行エージェントとしての能力も欲しい。特に秘書的な振る舞い。

## 現状分析（調査済み）

### 既にあるもの
- **社会性（`familiar_neighbor/mind/`）**: appraisal（PAD感情）/ social_policy（17発話行為×13応答モード）/ relationship（trust/intimacy + 傾向/境界/儀式）/ meta_monitor（応答ゲート）/ workspace（GWT競争）/ tom（ToM tool）/ scene（世界モデル）。豊富だが **一方向フロー**（入力→appraise→decide→出力）。
- **タスク**: `familiar_runtime/tasks/`（Task + checkpoint, 独自 `runtime_tasks.db`, self-init schema）。task-mode CLI 専用。
- **やり残し**: `ConcernEngine`（感情的テーマ, 自動decay, JSON）/ `unfinished_business`（memory DB, prompt に最大3件 surface）。

### 欠けているギャップ
1. **秘書の核がない**: 期日・優先度を持ち、due になったら**自発的に思い出す**「約束・予定・リマインダ」レイヤが無い。Task は期日/優先度/リマインダを持たず、プロンプトにも出ない。
2. **社会的学習ループが閉じてない**: `relationship.failed_support_patterns` を記録しても `social_policy.decide()` が参照せず、過去の失敗/成功が応答選択に反映されない。
3. **相手モデルが蓄積されない**: ToM は毎回 recall して推論するだけ。persistent な person model が無い。

## 設計方針

- 秘書能力は **persona非依存の汎用基盤** → `familiar_runtime/commitments/`（`tasks/` の先例に倣い独自DB self-init）。
- 社会性強化は **既存 mind/ レイヤの結線追加**（決定論ロジック優先、プロンプト肥大を避ける）。
- 各 Phase は独立 PR 相当、テスト緑を維持。TDD（RED→GREEN）。

---

## Phase 1 — Commitment ストア（秘書の核, 汎用基盤）✅

**新規** `src/familiar_runtime/commitments/`:
- `model.py`:
  - `CommitmentKind(str, Enum)`: REMINDER / APPOINTMENT / PROMISE / FOLLOWUP / TASK
  - `CommitmentStatus(str, Enum)`: OPEN / DONE / CANCELLED / SNOOZED
  - `@dataclass Commitment`: id, summary, kind, status, due_at(float|None), priority(int 0-3),
    created_by(str), person(str|None), created_at, updated_at, completed_at(float|None),
    snooze_until(float|None), metadata
  - helper: `is_due(now)`, `is_upcoming(now, horizon)`, `effective_due()`
- `store.py` `SQLiteCommitmentStore`（独自 `commitments.db`, self-init）:
  - create / save / get / update_status / complete / snooze / cancel
  - list_open / list_due(now) / list_upcoming(now, horizon)
  - 並び順: due_at（NULL は後ろ）, priority 降順, created_at
- `__init__.py` で re-export

**テスト** `tests/test_commitments.py`: create/reload, due 判定, upcoming 判定, snooze 復活,
complete, priority+due 並び順, cancelled 除外。

---

## Phase 2 — ツール + capability + 配線 + surface（秘書をエージェントに繋ぐ）✅

- **新規** `src/familiar_agent/tools/commitments.py` `CommitmentTool`（legacy tool 形式: `get_tool_definitions()` + async `call()`）:
  - `add_commitment`（summary, kind?, due_in_minutes?|due_at_iso?, priority?, person?）
  - `list_commitments`（filter: open/due/upcoming/all）
  - `complete_commitment`（id）
  - `snooze_commitment`（id, minutes）
- **新規** `src/familiar_capabilities/commitments.py` `CommitmentCapability(LegacyToolProvider)`
- **配線** `agent.py`: store/tool を `__init__` で構築、`_build_tool_registry()` で register
- **surface** `embodied_hook.py`: due + upcoming を continuity_ctx に注入（`unfinished_business` と同パターン、`[Reminders due]` / `[Upcoming]`）
- **テスト**: tool 単体 + capability spec + surface 文字列。

---

## Phase 3 — 自発的リマインド（due 検知 → proactive surface）

- `heartbeat` / continuation に「due commitment があれば次ターンで必ず言及 / 自発ターンを誘発」を接続。
- quiet hours（`routines.py`）尊重: quiet 中は緊急(priority>=2)以外は抑制。
- テスト: due ありで continuation/desire turn が誘発されること、quiet 中の抑制。

---

## Phase 4 — Person Model 永続化（社会性: ToM 蓄積）

- **新規** `src/familiar_neighbor/mind/person_model.py`: 相手ごとの推定（現在ニーズ/気分/最近の懸念/コミュニケーション好み）を時系列で保持（memory DB or 専用テーブル + migration）。
- `ToMTool` 結果を person_model に書き戻し、prompt に surface。
- テスト + migration。

---

## Phase 5 — 社会的学習ループを閉じる

- `relationship.failed_support_patterns` / 成功パターンを `SocialPolicyEngine.decide()` の入力に追加し、response_mode 選択を補正。
- 「以前これで失敗した」を避け「効いた」を優先。
- テスト: 同一状況で過去失敗パターンが response_mode を変えること。

---

## Validation（各 Phase 末）

```bash
uv run ruff check .
uv run ruff format --check .
uv run --group dev mypy src/familiar_agent src/familiar_runtime src/familiar_capabilities src/familiar_neighbor
uv run pytest -q
```

## 進行ステータス

- [x] Phase 1: Commitment ストア + tests（9件）
- [x] Phase 2: tool + capability + 配線 + surface + tests（13件）
- [ ] Phase 3: 自発的リマインド（continuation/desire-turn 機構に踏み込む。慎重に）
- [ ] Phase 4: Person Model
- [ ] Phase 5: 社会的学習ループ

本セッション: Phase 1–2 完遂。フルスイート **1007 passed**（+22）、ruff/format/mypy(116) 緑。
秘書の動く核（期日・優先度付き commitment を保存し、due になればターン文脈へ自動 surface）。

### Phase 3 設計メモ（次セッション）
due commitment があるとき、ユーザ入力が無くても自発ターンを誘発する。
`heartbeat`/desire-turn の起動条件に `commitment_store.list_due(now)` を加える。
quiet hours（`routines.py`）尊重 — quiet 中は priority>=2 のみ。
plan の codex待ち境界に近い fragile 領域なので、コウタが見てる時にやる。
