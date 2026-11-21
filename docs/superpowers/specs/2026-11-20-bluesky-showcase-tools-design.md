# Bluesky showcase tools: design

**Date:** 2026-11-20
**App:** `~/Projects/bluesky-siri` (Bluesky's open-source `social-app`, bundle `com.example.bskysiri`, `expo-syrup-ai-kit@0.4.0`)
**Kit:** this repo

## Why

The launch video's example is Wikipedia: one question, one answer, and the app opening at the highlighted answer. We want an example that shows more of what the kit can do, in a well-known app, without the person needing to sign in. Bluesky today has two generated public lookups (trending topics, profile by handle). That's no richer than Wikipedia.

## Goals

Each tool shows a different kit feature, and each passes a Siri evaluation on a phone:

| Feature | Tool | Example request |
|---|---|---|
| Parameters, value-only reply | `SearchAccounts(query)` | "In Bluesky, find accounts about astronomy." |
| Chaining two tools through an App Skill | `SearchAccounts` → `GetLatestPost(handle)`, skill `latest-post-by-name` | "In Bluesky, what did the New York Times post last?" |
| An `AppEntity` Siri resolves by name, indexed by identity only | `OpenProfile(account: AccountEntity)` | "Open NASA's profile in Bluesky." |
| Opening the app at the answer | `OpenProfile` (opens `bluesky://profile/<handle>`) | as above |
| A write action that asks to confirm | `DraftPost(text)` → confirmation → opens the composer filled in | "Post 'hello from Siri' on Bluesky." |

Plus, for each tool: five runs naming the app, and a negative control (an `EvalSwitch` that breaks the tool) that must fail.

## Non-goals

- Signed-in tools (notifications, messages, really posting, following). They're a later round and need sign-in shared with Swift.
- The `javascript` handler kind. It isn't built.
- Changing Bluesky's own features. The only app-side change is a debug-only `ToolOutcomeView`, if it isn't already there.

## Anti-goals

- **Answering from Spotlight.** If `AccountEntity` indexes follower counts or post text, Siri answers stale data without calling a tool. Index the DID, handle and display name only.
- **A dialog on a chained tool.** `SearchAccounts` and `GetLatestPost` return values only (`.result(value:)`). With a dialog Siri ends its turn and the chain breaks (app-skills spike, #31).
- **Implying Bluesky endorses this.** Same disclaimer rule as the Wikipedia clip.
- **Sending a post.** `DraftPost` only opens the composer. The person taps Post.

## Constraints found

- **Post search needs sign-in.** `app.bsky.feed.searchPosts` on `public.api.bsky.app` returns 403. That's why search is over accounts.
- **Public endpoints that work signed out** (checked 2026-11-20, all 200 in ~0.2 s): `app.bsky.actor.searchActors`, `app.bsky.feed.getAuthorFeed` (`filter=posts_no_replies`), `com.atproto.identity.resolveHandle`, `app.bsky.feed.getFeed`, `app.bsky.feed.getPostThread`, `app.bsky.actor.getProfile`.
- **The composer link exists:** `bluesky://intent/compose?text=…` (`src/lib/hooks/useIntentHandler.ts:85`). **It does nothing when signed out** (`if (!hasSession) return`, line 170), and the eval harness waits for the signed-out screen (`readyWhen: .label("createAccountText", …)`).
- **Signed out, the iOS app shows only the sign-in screen.** `src/view/shell/createNativeStackNavigatorWithAuth.tsx:124` returns `<LoggedOut />` for every route on native when there's no session. So `bluesky://profile/<handle>` also lands on sign-in, not only the composer. The API calls themselves work signed out.
- **The declaration can't describe a hand-written tool.** `siri-tools.json` entries must have `request` and `reply` (`expo-plugin/plugin/src/siriTools/declaration.ts`), and each one generates Swift.
- **Hand-written Swift already has a path: `expo-app-intents` inline modules.** Its `init` turns on inline modules and compiles `app-intents/*.swift` into the app (`expo-plugin/README.md`, "Install" and "A first tool"). Bluesky doesn't have `expo-app-intents` installed yet. *(An earlier draft said the plugin had no path. That was wrong: I'd read the plugin's code, not its README.)*
- **Evals check only tool calls and Siri's reply** (`SiriMetric.intents`, `.siriResponse`). They can't see what the app shows after the run.
- **`bluesky-siri` has 24 uncommitted files** (the bundle-ID and App Group rename). They're needed to build and stay as they are.
- **Siri's 10-second budget.** Chained runs take about 60 s overall, but each tool call must finish within 10 s.

## Approaches

1. **One kit feature per hand-written Swift tool (chosen).** Shows chaining, entities, opening the app and confirmation, none of which generated tools can do. Costs hand-written Swift and the plugin gap below.
2. **More generated tools in `siri-tools.json`.** Cheap and stays on the JSON path, but generated tools return a dialog, so they can't chain, open the app or confirm. It would be Wikipedia again with more lookups.
3. **Signed-in tools.** The most impressive, but it needs sign-in sharing first. Deferred.

## Design

### Tools

- **`SearchAccounts(query: String)`**: `searchActors?q=…&limit=3`. Value: "3 accounts: NASA (@nasa.gov), …". Value only.
- **`GetLatestPost(handle: String)`**: `getAuthorFeed?actor=…&limit=1&filter=posts_no_replies`. Value: who, how long ago in words, the text cut to ~150 characters, and the like count. Value only. No post: "@x hasn't posted yet."
- **`AccountEntity`**: `AppEntity` + `IndexedEntity`. `id` is the DID. Shows the display name and `@handle`. `EntityStringQuery` uses `searchActors`. `entities(for:)` uses `getProfiles`. Accounts the tools return are indexed with identity fields only.
- **`OpenProfile(account: AccountEntity)`**: `OpenIntent`. Opens `bluesky://profile/<handle>`. Returns a short dialog ("Opening NASA's profile.").
- **`DraftPost(text: String)`**: `requestConfirmation` first ("Draft this post in Bluesky: …?"). On yes, it opens `bluesky://intent/compose?text=…`. On no, nothing runs.
- **App Skill `latest-post-by-name`**: (1) search accounts with the person's words; (2) take the first handle; (3) get its latest post; (4) say who posted it and what it said.

Every tool goes through `SiriTool(appName: "Bluesky").answer`/`run`, so failures come back as sentences and outcomes are recorded.

### Code layout

- Request building and reply wording are pure functions (decoded JSON → sentence), unit-tested with `swift test` against saved API responses. The intents are thin.
- **Hand-written tools stay out of `siri-tools.json`** (my call). The validator needs `request`, and an entry would generate a second, clashing type. Each tool's title and description live in its Swift. A kind of entry that only declares the interface is a separate kit change, so it gets its own issue.
- **`SearchAccounts` stays hand-written** (my call). It could be generated with `"returns": "value"` and still chain, but it records the accounts it finds for `AccountEntity`'s index, and generated code can't.
- `EvalSwitch` definitions compile into both the app and the evals target, the way `Example/Shared/EvalSwitches.swift` does today. Where that file lives follows from open question 1.

### Evaluations (`siri-evals/BlueskyEvaluations.swift`)

One `ToolEvaluation` per row of the goals table, five runs each, naming the app. Reply checks use something only live data has (an `@` handle, "post"). Each tool gets one negative control through an `EvalSwitch` that points requests at an unreachable host.

## Decided by the owner (re-confirmed after the corrections)

1. **Tools go in through `expo-app-intents` inline modules,** the kit's documented path, in `app-intents/`. No kit change. The shared `EvalSwitches.swift` lives in `app-intents/`, and `siri-evals/` holds a symlink to it, so the evals target compiles the same file (my call).
2. **The eval phone is signed in to a throwaway test account,** so opening a profile or the composer really lands in the app. Evals check tool calls and Siri's replies. The screen the app lands on is checked by hand and in demo footage. The harness waits for the signed-in shell (the tool-outcome label, which is shown only there). The account's details stay on the phone and never go in the repo. `DraftPost` never sends anything.

Order of work: (1) `expo-app-intents` set up, plus the outcome label; (2) pure request and wording code, with `swift test` unit tests; (3) the intents, entity and skill; (4) the evals on the phone.

Out of scope (my call): negative controls for the two existing generated tools. Generated Swift has no `EvalSwitch` hook, so covering them means changing the code generator.

## Left to the builder

Exact wording of descriptions and replies within the rules above, test fixture capture, the `EvalSwitch` names, and whether `OpenProfile` also accepts a plain handle.
