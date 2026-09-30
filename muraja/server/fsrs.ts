import { createEmptyCard, fsrs, generatorParameters, Rating, State, type Card, type Grade } from 'ts-fsrs';
import { z } from 'zod';

/** User-tunable scheduler settings, persisted in users.settings. */
export const SchedulerSettings = z.object({
  request_retention: z.number().min(0.7).max(0.97).default(0.9),
  maximum_interval: z.number().int().min(7).max(36500).default(36500),
  enable_fuzz: z.boolean().default(true),
  new_per_day: z.number().int().min(0).max(200).default(15),
});
export type SchedulerSettings = z.infer<typeof SchedulerSettings>;
/** Partial update without defaults, so an absent field keeps its stored value. */
export const SchedulerPatch = z.object({
  request_retention: z.number().min(0.7).max(0.97).optional(),
  maximum_interval: z.number().int().min(7).max(36500).optional(),
  enable_fuzz: z.boolean().optional(),
  new_per_day: z.number().int().min(0).max(200).optional(),
});

export function schedulerFor(s: SchedulerSettings) {
  return fsrs(generatorParameters({
    request_retention: s.request_retention,
    maximum_interval: s.maximum_interval,
    enable_fuzz: s.enable_fuzz,
  }));
}

export interface StateRow {
  item_id: string; user_id: string; due: number; stability: number; difficulty: number;
  elapsed_days: number; scheduled_days: number; learning_steps: number; reps: number;
  lapses: number; state: number; last_review: number | null; last_rating: number | null; version: number;
}

export function emptyState(itemId: string, userId: string, now: number): StateRow {
  const c = createEmptyCard(new Date(now));
  return { item_id: itemId, user_id: userId, ...cardToCols(c), last_rating: null, version: 0 };
}

function cardToCols(c: Card) {
  return {
    due: c.due.getTime(), stability: c.stability, difficulty: c.difficulty, elapsed_days: c.elapsed_days,
    scheduled_days: c.scheduled_days, learning_steps: c.learning_steps, reps: c.reps, lapses: c.lapses,
    state: c.state as number, last_review: c.last_review ? c.last_review.getTime() : null,
  };
}

export function rowToCard(r: StateRow): Card {
  return {
    due: new Date(r.due), stability: r.stability, difficulty: r.difficulty, elapsed_days: r.elapsed_days,
    scheduled_days: r.scheduled_days, learning_steps: r.learning_steps, reps: r.reps, lapses: r.lapses,
    state: r.state as State, last_review: r.last_review == null ? undefined : new Date(r.last_review),
  };
}

export function applyRating(row: StateRow, grade: Grade, now: number, s: SchedulerSettings): StateRow {
  const { card } = schedulerFor(s).next(rowToCard(row), new Date(now), grade);
  return { ...row, ...cardToCols(card), last_rating: grade, version: row.version + 1 };
}

export { Rating, State };
export type { Grade };
