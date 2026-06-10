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

## Phase 3 — 自発的リマインド（実装済 ✅）

ユーザ確定: トグル独立・既定ON / quiet hours は priority>=2 のみ / だんだん間隔を空けて止まる。

- model: `last_reminded_at` / `reminder_count` / `due_for_reminder()`（backoff base×{1,3}, REMINDER_CAP=3 で沈黙。passive surface は継続）
- store: `_ensure_columns()` idempotent ALTER / `list_due_for_reminder` / `mark_reminded`（targeted UPDATE）/ `snooze` で cadence リセット
- config: `AgentConfig.proactive_reminders`（`FAMILIAR_PROACTIVE_REMINDERS`、既定 True、auto_desire 独立）+ settings_schema（advanced/bool）
- i18n: `reminder_impulse`（en/ja、他言語 en フォールバック）。complete/snooze ツール呼び出しまで指示
- `_ui_helpers`: `should_fire_commitment_reminder`（純粋ゲート: running/pending/idle-gap/quiet-priority）/ `commitment_reminder_prompt` / `decide_idle_action`
- 3ループ配線: main repl / tui `_reminder_tick` / gui `_process_queue` — いずれも **auto_desire ガードの前**
- テスト +33（store cadence・legacy DB 移行・ゲート全分岐・config 独立性・3ループ配線統合・mark-before-run 固定）

**多角レビュー（4次元×敵対検証）→ 確定 10 findings を全修正:**
- `mark_reminded` を**ターン前**に移動（3ループ）— ターン中の snooze による cadence リセットを保護、
  失敗時セマンティクス統一（エラーでもスロット消費 → flapping backend が cap で自己制限）
- TUI 二重 `agent.run` レース: `_process_queue` が `get()` 後に `_agent_running` ならキューへ差し戻し
  （実行中ターンが interrupt_queue 経由で吸収）
- REPL: reminder turn とゲート＋mark を try/except 保護（裸だと finally の `os._exit(0)` で silent death）、
  ターン後に `last_interaction_time` 更新（desire の連続発火防止）
- GUI/TUI: tick 本体（heartbeat/store 呼び出し）を例外ガード — sqlite エラーで idle ループが恒久死しない
- `due_for_reminder` の idx を `max(0, ...)` でクランプ + 不整合状態のテスト
- `decide_idle_action` docstring を実態（contract の参照実装）に修正
- 修正後に per-fix 敵対検証 7/7 resolved + completeness 残渣（mark ガード/GUI mark-before-run pin/clamp テスト）も解消

---

## Phase 4 — Person Model 永続化（社会性: ToM 蓄積）

**問題**: ToMTool の LLM 推論は構造化 JSON `{evidence, inference[{state,confidence}], policy}` を生成するのに
markdown に平坦化して捨てている（`_last_policy` のみ揮発保持）。相手の心的モデルが蓄積されない。

**設計**（RelationshipTracker の永続パターン踏襲: lazy conn + WAL + apply_migrations）:
- migration `2026-06-XX-010_person_models.py`: `person_inferences` テーブル
  （id TEXT PK, person TEXT, state TEXT, confidence REAL, evidence_json TEXT, policy TEXT,
  source TEXT default 'tom', created_at TEXT ISO）+ person/created_at index。observations.db に同居。
- **新規** `src/familiar_neighbor/mind/person_model.py` `PersonModelTracker`:
  `record_inference(person, states, evidence, policy)` / `recent(person, n)` /
  `context_for_prompt(person)` → `[Person model: X]` ブロック（最近の推定＋確信度＋最後に効いた方針、recency 順）
- `ToMTool`: `_llm_inference` で JSON parse 成功時に tracker へ書き戻し（optional 依存、None なら従来挙動）
- `agent.py`: tracker 構築 → ToMTool へ注入。`embodied_hook.prepare_turn` で companion の
  `context_for_prompt` を relationship ctx の隣に注入
- テスト: tracker CRUD/プロンプト整形/migration 適用（test_memory_migrations.py パターン）/
  ToM 書き戻し（fake backend が JSON 返却）/ hook surface

---

## Phase 5 — 社会的学習ループを閉じる（実装済 ✅）

記録するだけで参照されなかった `failed_support_patterns` / `support_preferences` を
`SocialPolicyEngine.decide()` に接続。決定論補正 `_apply_relationship_learning`:
- アドバイス系失敗履歴（advice/solution/正論/説教 等のマーカー）or validate-first 系 style を検知したら:
  - distress 系 act（venting/fatigue/grief/conflict）→ `should_recall_relational_memory=True`
    （relational ctx に失敗パターンが描画されるのでモデルが「前に失敗したこと」を見る）+ softness 微増
  - 明示的依頼（request_for_advice/action）→ 依頼は尊重しつつ `should_use_tom=True` +
    directness 減・softness 増（validate-first な伝え方へ）
- `relationship_learning_inputs()` が Tracker のアイテム形状（style / pattern|evidence）を吸収（契約テスト付き）
- `embodied_hook.prepare_turn` の decide() 呼び出しに配線
- テスト +7（無履歴で不変・和文マーカー・無関係パターン不発・契約）

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
- [x] Phase 3: 自発的リマインド（独立トグル・quiet hours・escalating backoff+cap、3ループ配線、レビュー10件全修正）
- [x] Phase 4: Person Model（person_inferences + PersonModelTracker + ToM 書き戻し + prompt surface）
- [x] Phase 5: 社会的学習ループ（failed patterns → decide() 補正、契約テスト付き）

**PR #175 作成済み**（https://github.com/lifemate-ai/familiar-ai/pull/175、develop 向け）。
CI 全緑（lint + test macos/ubuntu/windows）。**merge はコウタ判断。**
全5フェーズ完了 + アジェンダ + staleness カットオフ + CLAUDE.md 更新 + レビュー指摘全消化。

---

## PR ドラフト（コウタ用 — push 後にそのまま使える）

**タイトル:** `feat: secretary layer (commitments + proactive reminders) and social accumulation (person model + learned policy)`

**本文:**

```markdown
## Summary

Two pillars toward "more human, more socially capable":

**Secretary layer** — the agent can now hold commitments (reminders,
appointments, promises, follow-ups) with due times and priorities, surface
them passively in every turn, proactively speak up when they come due
(independent of auto_desire, FAMILIAR_PROACTIVE_REMINDERS, default ON,
quiet-hours aware, escalating backoff capped at 3), and open the day with a
[Today's agenda] block on the first turn.

**Social accumulation** — ToM inferences now persist per person
(person_inferences, migration 010) and surface as an accumulated
[Person model] block (7-day staleness cutoff); recorded support failures
and preferences now feed back into SocialPolicyEngine.decide() so the same
support misstep is not repeated.

## Hardening

All three idle loops were wired through multi-agent adversarial review;
11 confirmed findings fixed and re-verified, including: mark-before-run
(mid-turn snooze survives), TUI concurrent agent.run race (re-queue for
interrupt drain), REPL silent-death via os._exit(0) on backend errors,
person-key fragmentation (canonicalization + COLLATE NOCASE).

## Tests

+87 tests across store cadence/backoff, legacy-DB migration, idle-loop
wiring (REPL/TUI/GUI), config independence, person-model roundtrip and
writeback isolation, social-policy learning invariance. Full suite
1070 passed; ruff/format/mypy green.
```
