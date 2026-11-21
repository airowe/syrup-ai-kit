# Bluesky Showcase Tools Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Four hand-written Siri tools, an `AccountEntity` and an App Skill in the Bluesky app. Each one shows a different Syrup AI Kit feature, and each is proven by Siri evaluations on a phone.

**Architecture:** Swift in `app-intents/`, compiled into the app by `expo-app-intents` inline modules. Request URLs, decoding and reply wording are pure Foundation code in `app-intents/Bluesky*.swift`, unit-tested by a small SwiftPM package in `siri-tests/` that symlinks those files. Intents are thin wrappers over `SiriTool`. Evaluations extend `siri-evals/BlueskyEvaluations.swift`.

**Tech Stack:** Swift 6, App Intents (iOS 27.3 Siri AI preview), SyrupAIKit / SyrupAIEvalKit 0.4.x, `expo-syrup-ai-kit@0.4.0`, `expo-app-intents`, Swift Testing, Expo 58.

**Spec:** `docs/superpowers/specs/2026-11-20-bluesky-showcase-tools-design.md` (this repo).

**Where the work happens:** `~/Projects/bluesky-siri`, on a new local branch `feat/siri-showcase-tools`. Its only remote is `bluesky-social/social-app`: **never push it.** Every commit step needs Adam's approval first (his global rule).

## Global Constraints

- Public host only: `https://public.api.bsky.app/xrpc/`. No credentials in any tool.
- Bundle `com.example.bskysiri`, App Group `group.com.example.bskysiri` (uncommitted rename, left as is).
- Every file in `app-intents/` imports SyrupAIKit as a plain `import SyrupAIKit`, never `internal import` (plugin README).
- `SearchAccounts` and `GetLatestPost` return `.result(value:)` only, with no `ProvidesDialog`.
- Replies are one spoken sentence, under about 200 characters, with no ids, URIs or raw dates.
- `AccountEntity` indexes DID, handle and display name only. Never follower counts or post text.
- `DraftPost` calls `requestConfirmation` before `tool.answer`, and only ever opens the composer. It never posts.
- Tool titles and descriptions are written once in Swift. Hand-written tools are not added to `siri-tools.json`.
- Eval switch reads sit inside `#if DEBUG || SIRI_AI_EVAL_SWITCHES`.
- Test-account credentials never go in the repo.

## Review Focus

1. **A handle said with `@`, in capitals or with spaces** ("@NASA.gov ") → treated as `nasa.gov`. Pinned in Task 2 (`normalizedHandle`).
2. **A handle that doesn't exist** (getAuthorFeed returns 400 `InvalidRequest`) → "Couldn't find @x on Bluesky.", not "Bluesky couldn't do that right now." Pinned in Task 2 (`describeLookupFailure`) and Task 4.
3. **Post text with newlines, emoji or a long URL** → newlines become spaces, and the cut falls on a whole character with "…". Pinned in Task 2.
4. **Draft text with `&`, `#`, `?`, `+` or `=`** → reaches the composer unchanged. Pinned in Task 2 (`composeURL`).
5. **An account with no display name, or an empty one** → named by `@handle` alone. Pinned in Task 2.

---

### Task 1: expo-app-intents and the tool-outcome label

**Files:**
- Modify: `package.json`, `app.config.js` (plugins, in the order `expo-app-intents`, then `expo-syrup-ai-kit`, with `skills: {sourceDir: 'siri-skills'}` added in Task 5)
- Create: `app-intents/AppIntentsSetup.swift` (from `npx expo-app-intents init --examples minimal`, then edited)
- Create: `src/lib/siri/SiriToolOutcome.tsx`
- Modify: the signed-in shell root (`src/view/shell/index.tsx`, inside the signed-in branch), rendering `<SiriToolOutcome />` under `__DEV__` only

**Interfaces:**
- Produces: the native module `AppIntentsSetup`, whose `siriToolOutcome(): string` returns `ToolOutcomeLog.label()` (so it starts with "Tool calls: "). The view `testID="siri-ai-tool-outcome"` exists only while signed in.

- [ ] **Step 1:** `git switch -c feat/siri-showcase-tools`, then `npx expo install expo-app-intents` and `npx expo-app-intents init --examples minimal`. Remove any example intent files `init` writes other than `AppIntentsSetup.swift`.
- [ ] **Step 2:** Make `siriToolOutcome` return `ToolOutcomeLog.label()`. Write `SiriToolOutcome.tsx` as in the plugin README's "Showing the tool's outcome", rendering the returned string, and mount it.
- [ ] **Step 3: Verify.** Run `SIRI_AI_PREVIEW=1 CP_CACHE_DIR="$PWD/.cp-cache" LANG=en_US.UTF-8 npx expo prebuild -p ios`, then `xcodebuild -workspace ios/Bluesky.xcworkspace -scheme Bluesky -destination 'generic/platform=iOS Simulator' build`. Expected: `BUILD SUCCEEDED`, and `AppIntentsSetup.swift` appears in the build log. Run `pnpm typecheck` and `pnpm lint`: both clean.
- [ ] **Step 4: Commit (after approval).** The 24 rename files come first, as their own commit `chore: rename bundle and app group for Siri testing`. Then `feat(siri): add expo-app-intents and tool outcome label`.

### Task 2: Pure request and wording code, with unit tests

**Files:**
- Create: `app-intents/BlueskyAPI.swift`: URLs and `Decodable` models.
- Create: `app-intents/BlueskyWording.swift`: sentences.
- Create: `siri-tests/Package.swift` (tools 6.0, macOS 14, library target `BlueskySiriCore` at `Sources/BlueskySiriCore`, test target `BlueskySiriCoreTests`).
- Create: `siri-tests/Sources/BlueskySiriCore/BlueskyAPI.swift` and `BlueskyWording.swift`: **symlinks** to `../../../app-intents/…`.
- Create: `siri-tests/Tests/BlueskySiriCoreTests/{APITests,WordingTests}.swift` and `Fixtures/{searchActors-nasa,authorFeed-nytimes,authorFeed-empty}.json`. These are real responses, captured with `curl` on the day.

**Interfaces (Produces):**
```swift
enum BlueskyAPI {
  static let publicHost: URL                                   // https://public.api.bsky.app/xrpc/
  static func searchActors(query: String, limit: Int = 3, host: URL = publicHost) -> URL
  static func authorFeed(handle: String, host: URL = publicHost) -> URL   // limit=1, filter=posts_no_replies
  static func profiles(dids: [String], host: URL = publicHost) -> URL     // app.bsky.actor.getProfiles, actors=…
  static func profileURL(handle: String) -> URL                // bluesky://profile/<handle>
  static func composeURL(text: String) -> URL                  // bluesky://intent/compose?text=<encoded>
}
struct Actor: Decodable, Equatable { let did: String; let handle: String; let displayName: String? }
struct ActorSearch: Decodable { let actors: [Actor] }
struct Profiles: Decodable { let profiles: [Actor] }
struct AuthorFeed: Decodable { let feed: [Item]; struct Item: Decodable { let post: Post } }
struct Post: Decodable { let author: Actor; let record: Record; let likeCount: Int?
  struct Record: Decodable { let text: String; let createdAt: Date } }   // decode with .iso8601 (fractional seconds allowed)
func normalizedHandle(_ spoken: String) -> String
func accountName(_ actor: Actor) -> String                     // "NASA (@nasa.gov)" or "@nasa.gov"
func describeAccounts(_ actors: [Actor], query: String) -> String
func describeLatestPost(_ feed: AuthorFeed, handle: String, now: Date) -> String
func describeLookupFailure(handle: String) -> String
```

- [ ] **Step 1: Write the failing tests.** Use Swift Testing. Parameterize with `@Test(arguments:)` wherever a table fits. Expected values:
  - `normalizedHandle`: `"@NASA.gov "` → `"nasa.gov"`, `"nasa.gov"` → `"nasa.gov"`.
  - `searchActors(query: "new york times")` has query items `q=new york times` and `limit=3`, and its host is the public one. Passing `host:` changes the host only.
  - `composeURL(text:)`: for each of `"a & b"`, `"#tag"`, `"why?"`, `"1+1=2"` and `"héllo 👋"`, read `text` back with `URLComponents` and check it round-trips exactly.
  - `profileURL(handle: "nasa.gov").absoluteString == "bluesky://profile/nasa.gov"`.
  - `accountName`: displayName `"NASA"` → `"NASA (@nasa.gov)"`. nil → `"@nasa.gov"`. `"  "` → `"@nasa.gov"`.
  - `describeAccounts([], query: "zzz")` == `"No Bluesky accounts match \"zzz\"."`
  - `describeAccounts` with 1 account == `"Found 1 account: NASA (@nasa.gov)."`. With 5 accounts, it names only the first 3: `"Found 5 accounts: A (@a), B (@b), C (@c)."`
  - `describeLatestPost(empty, handle: "x.bsky.social", now:)` == `"@x.bsky.social hasn't posted yet."`
  - `describeLatestPost` from the fixture, with `now` = createdAt + 2 h: it starts `"<Name> (@nytimes.com) posted 2 hours ago: \""` and ends `" It has <likeCount> likes."` (`1 like` when the count is 1, `no likes` when it's nil or 0).
  - Post text that has `\n\n` gets single spaces. Text over 150 characters is cut at the last space at or before 150, then `…`, and the result is still valid when the cut is next to an emoji. Empty text → `posted 2 hours ago: a post with no text.`
  - Age wording: < 1 min `just now`; minutes, hours and days, singular and plural; ≥ 7 days → `on <MMM d>`.
  - `describeLookupFailure(handle: "nope.example")` == `"Couldn't find @nope.example on Bluesky."`
  - Decoding each fixture succeeds. `AuthorFeed` from `authorFeed-nytimes.json` has 1 item.
- [ ] **Step 2:** `swift test --package-path siri-tests` → FAIL (symbols not defined).
- [ ] **Step 3:** Implement the two files. Use `RelativeDateTimeFormatter` only if its output matches the pinned strings. Otherwise write the wording directly.
- [ ] **Step 4:** `swift test --package-path siri-tests` → all pass. Then rerun the Task 1 `xcodebuild` to confirm the inline module still builds with the new files. Expected: `BUILD SUCCEEDED`. If inline modules reject a file, stop and report: the layout decision depends on it.
- [ ] **Step 5: Commit (after approval):** `feat(siri): add Bluesky request and reply wording`.

### Task 3: Client, eval switch and AccountEntity

**Files:**
- Create: `app-intents/EvalSwitches.swift`: `extension EvalSwitch { static let badHost: EvalSwitch = "bad-host" }`.
- Create: `siri-evals/EvalSwitches.swift`: a symlink to `../app-intents/EvalSwitches.swift`.
- Create: `app-intents/BlueskyClient.swift`.
- Create: `app-intents/AccountEntity.swift`.

**Interfaces:**
- Consumes: Task 2's `BlueskyAPI`, models and wording.
- Produces:
```swift
let blueskyTool: SiriTool              // SiriTool(appName: "Bluesky", classify: { ($0 as? AccountNotFound).map { _ in .failed } })
struct AccountNotFound: Error { let handle: String }
enum BlueskyClient {
  static var host: URL                 // publicHost, or https://bluesky-eval.invalid/xrpc/ when .badHost is on (inside #if DEBUG || SIRI_AI_EVAL_SWITCHES)
  static func searchActors(_ query: String) async throws -> [Actor]
  static func latestPost(handle: String) async throws -> AuthorFeed   // HTTP 400 → throws AccountNotFound
  static func profiles(dids: [String]) async throws -> [Actor]
}
struct AccountEntity: AppEntity, IndexedEntity   // id = did; displayRepresentation title = display name or @handle, subtitle = @handle
struct AccountQuery: EntityStringQuery          // entities(matching:) → searchActors; entities(for:) → profiles
enum AccountIndex { static func index(_ actors: [Actor]) async }  // CSSearchableIndex via indexAppEntities; identity fields only
```
- Non-2xx responses other than 400 throw `URLError(.badServerResponse)`, which counts as `.failed`.

- [ ] **Step 1:** Write the files. They contain no logic beyond what Task 2 tested, so there's no new unit test. The checks are the build and Task 6's evals.
- [ ] **Step 2: Verify:** prebuild and `xcodebuild` as in Task 1 → `BUILD SUCCEEDED`. Then check the evals target compiles the symlinked switch: `xcodebuild … -scheme BlueskyEvals build-for-testing`. Expected: `TEST BUILD SUCCEEDED`.
- [ ] **Step 3: Commit (after approval):** `feat(siri): add Bluesky client, eval switch and account entity`.

### Task 4: The four intents

**Files:** Create `app-intents/{SearchAccountsIntent,GetLatestPostIntent,OpenProfileIntent,DraftPostIntent}.swift`. Each one is wrapped in `#if SIRI_AI_PREVIEW @AppIntent(.tool) #endif`.

| Type | title | description | Parameters | Returns |
|---|---|---|---|---|
| `SearchAccountsIntent` | Search Accounts | Finds Bluesky accounts by name or topic and lists up to three, with their handles. | `query: String` ("Search For") | `ReturnsValue<String>`. Indexes the found actors through `AccountIndex` after answering, without awaiting it inside the budget. |
| `GetLatestPostIntent` | Get Latest Post | Says what a Bluesky account posted most recently, given its handle, like "nytimes.com". | `handle: String` ("Handle") | `ReturnsValue<String>`. `AccountNotFound` → `describeLookupFailure`, returned from inside `answer` with `ToolOutcomeLog.standard.note("not found")`. |
| `OpenProfileIntent` (`OpenIntent`) | Open Profile | Opens a Bluesky account's profile in the app. | `target: AccountEntity` ("Account") | dialog `"Opening <accountName>'s profile."`. Opens `profileURL` with `openURL`. |
| `DraftPostIntent` | Draft Post | Drafts a Bluesky post with the given text and opens it in the composer, ready for the person to post. | `text: String` ("Text") | `requestConfirmation(actionName: .post, dialog: "Draft this Bluesky post: \"<text>\"?")` before anything else. Then it opens `composeURL` and gives the dialog `"It's in the composer. Tap Post when you're ready."` |

- [ ] **Step 1:** Write the four intents.
- [ ] **Step 2: Verify:** prebuild and build → `BUILD SUCCEEDED`. Then `grep -c '"identifier"' ios/build/…/Metadata.appintents/extract.actionsdata` or use `appintentsmetadataprocessor` output: all four intent identifiers and `AccountEntity` are present.
- [ ] **Step 3: Commit (after approval):** `feat(siri): add search, latest post, open profile and draft post tools`.

### Task 5: App Skill `latest-post-by-name`

**Files:** Create `siri-skills/latest-post-by-name/SKILL.md`. Modify `app.config.js`: add `skills: {sourceDir: 'siri-skills'}` to the `expo-syrup-ai-kit` options.

- [ ] **Step 1:** Frontmatter: `name: latest-post-by-name` and a `description` ("When someone asks what a Bluesky account posted, by its name rather than its handle"). Body, the 4 steps from the spec: search with the person's words; take the first account's handle; get its latest post; say who posted it and what it said.
- [ ] **Step 2: Verify:** prebuild → no plugin errors. The build log has a `ProcessSkillsBundle` step, and `Skills.skillsc` exists in `Metadata.appintents`.
- [ ] **Step 3: Commit (after approval):** `feat(siri): add latest-post-by-name skill`.

### Task 6: Evaluations on a signed-in phone

**Files:** Modify `siri-evals/BlueskyEvaluations.swift`.

**Interfaces:** Consumes the intent type names from Task 4 (`intents["SearchAccountsIntent"]` and so on) and `EvalSwitch.badHost` from Task 3.

- [ ] **Step 1:** Change the harness to `readyWhen: .labelBegins(ToolOutcomeLog.accessibilityIdentifier, with: "Tool calls:")`. Keep the two existing evals.
- [ ] **Step 2:** Add evals, 5 runs each:
  - "In Bluesky, find accounts about astronomy." → calls `searchAccounts`; reply contains `@`.
  - "In Bluesky, what did the New York Times post last?" → calls `searchAccounts` then `getLatestPost`; reply contains "post" (case-insensitive).
  - "Open NASA's profile in Bluesky." → calls `openProfile`.
  - "Post 'hello from Siri' on Bluesky.", answered "Yes" → calls `draftPost`. Use the kit's confirmation pattern from the Example (`CartEvaluationTests.swift`).
  - The same request answered "No" → reply doesn't contain "composer", and the composer never opens (checked by hand once in Step 4).
  - Negative controls with `.negativeControl(turningOn: .badHost)` for `searchAccounts` and `getLatestPost` → reply check `expectAllFail(.siriResponse)` on `@` and "post".
- [ ] **Step 3: Run on Adam's phone.** It must be signed in to the test account, on iOS 27.3. Run `xcodebuild test -scheme BlueskyEvals -destination 'platform=iOS,name=<phone>'`, then `syrup-ai-eval summarize --fail-on real <xcresult>`. Expected: every positive eval 5 of 5, every negative control fails as intended. Record the table in `siri-evals/README.md`. **Stop and report** if any eval is below 5 of 5. Don't retune descriptions without asking.
- [ ] **Step 4: Check by hand:** "Open NASA's profile" lands on the profile, and "Yes" to the draft opens the composer with the text. Record both as checked by hand.
- [ ] **Step 5: Commit (after approval):** `test(siri): evaluate showcase tools on a device`.
