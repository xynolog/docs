// Ambient vocabulary for the agent skills' code fences (builder/skills).
//
// A skill teaches a script in pieces: the first fence signs in, and the ones
// after it use what that fence made. Each fence is checked as a module of its
// own, so the names that carry from one fence to the next are declared here,
// typed against the real surface. Everything else a fence uses it imports or
// declares itself, as the script it teaches would.
import type {
  KbTarget as _KbTarget,
  OpenedSession as _OpenedSession,
  XynologSession as _XynologSession,
  XynologClient as _XynologClient,
  ResourceId as _ResourceId,
} from '@xynolog/sdk';

declare global {
  /** The knowledge base the skill's setup fence signs in to. */
  const kb: _KbTarget;
  /** What the skill's setup fence's sign-in gave: the session and the client it was built with. */
  const opened: _OpenedSession;
  /** The session the skill's setup fence signed in. */
  const session: _XynologSession;
  /** That session's client. */
  const xynolog: _XynologClient;
  /** The resource the skill is working on. */
  const rId: _ResourceId;
}

export {};
