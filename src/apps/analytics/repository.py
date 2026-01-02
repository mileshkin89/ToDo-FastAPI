from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class AnalyticsRepository:

    @staticmethod
    async def get_global_counters(db: AsyncSession) -> dict:
        query = text("""
            SELECT
                COUNT(*) AS total_tasks,
                COUNT(*) FILTER (WHERE completed = false) AS active_tasks,
                COUNT(*) FILTER (WHERE completed = true) AS completed_tasks,
                COUNT(*) FILTER (
                    WHERE due_date < NOW()
                    AND completed = false
                ) AS overdue_tasks,
                (
                    SELECT COUNT(*)
                    FROM users
                ) AS total_users
            FROM tasks
        """)

        result = await db.execute(query)
        row = result.mappings().one()

        return dict(row)


    @staticmethod
    async def get_tasks_last_24_hours(db: AsyncSession) -> list[dict]:
        query = text("""
            WITH hours AS (
                SELECT
                    generate_series(
                        date_trunc('hour', NOW()) - INTERVAL '23 hours',
                        date_trunc('hour', NOW()),
                        INTERVAL '1 hour'
                    ) AS hour
            )
            SELECT
                h.hour AS day,

                COUNT(t.id) FILTER (
                    WHERE t.created_at >= h.hour
                      AND t.created_at < h.hour + INTERVAL '1 hour'
                ) AS created_tasks,

                COUNT(t.id) FILTER (
                    WHERE t.completed = false
                      AND t.created_at <= h.hour
                ) AS active_tasks,

                COUNT(t.id) FILTER (
                    WHERE t.completed = true
                      AND t.completed_at >= h.hour
                      AND t.completed_at < h.hour + INTERVAL '1 hour'
                ) AS completed_tasks,

                COUNT(t.id) FILTER (
                    WHERE t.completed = false
                      AND t.due_date IS NOT NULL
                      AND t.due_date < h.hour
                ) AS overdue_tasks

            FROM hours h
            LEFT JOIN tasks t ON (
                t.created_at <= h.hour + INTERVAL '1 hour'
            )
            GROUP BY h.hour
            ORDER BY h.hour
        """)

        result = await db.execute(query)
        return [dict(row) for row in result.mappings().all()]


    @staticmethod
    async def get_tasks_last_7_days(db: AsyncSession) -> list[dict]:
        query = text("""
            WITH days AS (
                SELECT
                    generate_series(
                        (CURRENT_DATE - INTERVAL '6 days')::date,
                        CURRENT_DATE::date,
                        INTERVAL '1 day'
                    )::date AS day
            )
            SELECT
                d.day AS day,

                COUNT(t.id) FILTER (
                    WHERE t.created_at::date = d.day
                ) AS created_tasks,

                COUNT(t.id) FILTER (
                    WHERE t.completed = false
                      AND t.created_at::date <= d.day
                ) AS active_tasks,

                COUNT(t.id) FILTER (
                    WHERE t.completed = true
                      AND t.completed_at::date = d.day
                ) AS completed_tasks,
                
                 COUNT(t.id) FILTER (
                    WHERE t.completed = false
                      AND t.due_date IS NOT NULL
                      AND t.due_date::date < d.day
                ) AS overdue_tasks

            FROM days d
            LEFT JOIN tasks t ON (
                t.created_at::date <= d.day
            )
            GROUP BY d.day
            ORDER BY d.day
        """)

        result = await db.execute(query)
        return [dict(row) for row in result.mappings().all()]


    @staticmethod
    async def get_tasks_last_4_weeks(db: AsyncSession) -> list[dict]:
        query = text("""
            WITH weeks AS (
                SELECT
                    generate_series(
                        date_trunc('week', NOW()) - INTERVAL '4 weeks',
                        date_trunc('week', NOW()),
                        INTERVAL '1 week'
                    )::date AS week_start
            )
            SELECT
                w.week_start AS day,

                COUNT(t.id) FILTER (
                    WHERE t.created_at >= w.week_start
                      AND t.created_at < w.week_start + INTERVAL '1 week'
                ) AS created_tasks,

                COUNT(t.id) FILTER (
                    WHERE t.completed = false
                      AND t.created_at < w.week_start + INTERVAL '1 week'
                ) AS active_tasks,

                COUNT(t.id) FILTER (
                    WHERE t.completed = true
                      AND t.completed_at >= w.week_start
                      AND t.completed_at < w.week_start + INTERVAL '1 week'
                ) AS completed_tasks,

                COUNT(t.id) FILTER (
                    WHERE t.completed = false
                      AND t.due_date IS NOT NULL
                      AND t.due_date < w.week_start + INTERVAL '1 week'
                ) AS overdue_tasks

            FROM weeks w
            LEFT JOIN tasks t
                ON t.created_at < w.week_start + INTERVAL '1 week'
            GROUP BY w.week_start
            ORDER BY w.week_start
        """)

        result = await db.execute(query)
        return [dict(row) for row in result.mappings().all()]


class UserAnalyticsRepository:

    @staticmethod
    async def get_user_analytics(
        db: AsyncSession,
        user_id: int,
    ) -> dict:
        query = text("""
            SELECT
                CAST(:user_id AS INTEGER) AS user_id,
                COUNT(*) AS total_tasks,
                COUNT(*) FILTER (WHERE completed = false) AS active_tasks,
                COUNT(*) FILTER (WHERE completed = true) AS completed_tasks,
                COUNT(*) FILTER (
                    WHERE completed = false
                    AND due_date IS NOT NULL
                    AND due_date < NOW()
                ) AS overdue_tasks,
                ROUND(
                    CASE
                        WHEN COUNT(*) = 0 THEN 0
                        ELSE
                            COUNT(*) FILTER (
                                WHERE completed = false
                                AND due_date IS NOT NULL
                                AND due_date < NOW()
                            ) * 100.0 / COUNT(*)
                    END,
                    2
                ) AS overdue_percent
            FROM tasks
            WHERE user_id = :user_id
        """)

        result = await db.execute(query, {"user_id": user_id})
        return dict(result.mappings().one())

    @staticmethod
    async def get_user_tasks_last_24_hours(
            db: AsyncSession,
            user_id: int,
    ) -> list[dict]:
        query = text("""
            WITH hours AS (
                SELECT generate_series(
                    date_trunc('hour', NOW()) - INTERVAL '23 hours',
                    date_trunc('hour', NOW()),
                    INTERVAL '1 hour'
                ) AS hour
            )
            SELECT
                CAST(:user_id AS INTEGER) AS user_id,
                h.hour AS day,

                -- created_tasks reflects tasks created during the hour
                COUNT(t.id) FILTER (
                    WHERE t.created_at >= h.hour
                      AND t.created_at < h.hour + INTERVAL '1 hour'
                ) AS created_tasks,

                -- active_tasks reflects tasks that are active (not completed) at the end of the hour
                COUNT(t.id) FILTER (
                    WHERE t.created_at < h.hour + INTERVAL '1 hour'
                      AND (
                          t.completed_at IS NULL
                          OR t.completed_at >= h.hour + INTERVAL '1 hour'
                      )
                ) AS active_tasks,

                -- completed_tasks reflects tasks completed during the hour
                COUNT(t.id) FILTER (
                    WHERE t.completed = true
                      AND t.completed_at >= h.hour
                      AND t.completed_at < h.hour + INTERVAL '1 hour'
                ) AS completed_tasks,

                -- overdue_tasks reflects tasks overdue at the end of the hour
                COUNT(t.id) FILTER (
                    WHERE t.due_date IS NOT NULL
                      AND t.due_date < h.hour + INTERVAL '1 hour'
                      AND (
                          t.completed_at IS NULL
                          OR t.completed_at >= h.hour + INTERVAL '1 hour'
                      )
                ) AS overdue_tasks,

                ROUND(
                    CASE
                        WHEN COUNT(t.id) = 0 THEN 0
                        ELSE
                            COUNT(t.id) FILTER (
                                WHERE t.due_date IS NOT NULL
                                  AND t.due_date < h.hour + INTERVAL '1 hour'
                                  AND (
                                      t.completed_at IS NULL
                                      OR t.completed_at >= h.hour + INTERVAL '1 hour'
                                  )
                            ) * 100.0 / COUNT(t.id)
                    END,
                    2
                ) AS overdue_percent

            FROM hours h
            LEFT JOIN tasks t
                ON t.user_id = :user_id
               AND t.created_at < h.hour + INTERVAL '1 hour'
            GROUP BY h.hour
            ORDER BY h.hour
        """)

        result = await db.execute(query, {"user_id": user_id})
        return [dict(row) for row in result.mappings().all()]

    @staticmethod
    async def get_user_tasks_last_7_days(
        db: AsyncSession,
        user_id: int,
    ) -> list[dict]:
        query = text("""
            WITH days AS (
                SELECT generate_series(
                    CURRENT_DATE - INTERVAL '6 days',
                    CURRENT_DATE,
                    INTERVAL '1 day'
                )::date AS day
            )
            SELECT
                CAST(:user_id AS INTEGER) AS user_id,
                d.day,

                -- created_tasks reflects tasks created during the day
                COUNT(t.id) FILTER (
                    WHERE DATE(t.created_at) = d.day
                ) AS created_tasks,

                -- active_tasks reflects tasks that are active (not completed) at the end of the day
                COUNT(t.id) FILTER (
                    WHERE t.created_at < d.day + INTERVAL '1 day'
                      AND (
                          t.completed_at IS NULL
                          OR t.completed_at >= d.day + INTERVAL '1 day'
                      )
                ) AS active_tasks,

                -- completed_tasks reflects tasks completed during the day
                COUNT(t.id) FILTER (
                    WHERE t.completed = true
                      AND DATE(t.completed_at) = d.day
                ) AS completed_tasks,
                
                -- overdue_tasks reflects tasks overdue at the end of the day
                COUNT(t.id) FILTER (
                    WHERE t.due_date IS NOT NULL
                      AND t.due_date < d.day + INTERVAL '1 day'
                      AND (
                          t.completed_at IS NULL
                          OR t.completed_at >= d.day + INTERVAL '1 day'
                      )
                ) AS overdue_tasks,

                ROUND(
                    CASE
                        WHEN COUNT(t.id) = 0 THEN 0
                        ELSE
                            COUNT(t.id) FILTER (
                                WHERE t.due_date IS NOT NULL
                                  AND t.due_date < d.day + INTERVAL '1 day'
                                  AND (
                                      t.completed_at IS NULL
                                      OR t.completed_at >= d.day + INTERVAL '1 day'
                                  )
                            ) * 100.0 / COUNT(t.id)
                    END,
                    2
                ) AS overdue_percent

            FROM days d
            LEFT JOIN tasks t
                ON t.user_id = :user_id
               AND t.created_at < d.day + INTERVAL '1 day'
            GROUP BY d.day
            ORDER BY d.day
        """)

        result = await db.execute(query, {"user_id": user_id})
        return [dict(row) for row in result.mappings().all()]

    @staticmethod
    async def get_user_tasks_last_4_weeks(
            db: AsyncSession,
            user_id: int,
    ) -> list[dict]:
        query = text("""
            WITH weeks AS (
                SELECT generate_series(
                    date_trunc('week', NOW()) - INTERVAL '4 weeks',
                    date_trunc('week', NOW()),
                    INTERVAL '1 week'
                ) AS week_start
            )
            SELECT
                CAST(:user_id AS INTEGER) AS user_id,
                w.week_start::date AS day,

                -- created_tasks reflects tasks created during the week
                COUNT(t.id) FILTER (
                    WHERE t.created_at >= w.week_start
                      AND t.created_at < w.week_start + INTERVAL '1 week'
                ) AS created_tasks,

                -- active_tasks reflects tasks that are active (not completed) at the end of the week
                COUNT(t.id) FILTER (
                    WHERE t.created_at < w.week_start + INTERVAL '1 week'
                      AND (
                          t.completed_at IS NULL
                          OR t.completed_at >= w.week_start + INTERVAL '1 week'
                      )
                ) AS active_tasks,

                -- completed_tasks reflects tasks completed during the week
                COUNT(t.id) FILTER (
                    WHERE t.completed = true
                      AND t.completed_at >= w.week_start
                      AND t.completed_at < w.week_start + INTERVAL '1 week'
                ) AS completed_tasks,

                -- overdue_tasks reflects tasks overdue at the end of the week
                COUNT(t.id) FILTER (
                    WHERE t.due_date IS NOT NULL
                      AND t.due_date < w.week_start + INTERVAL '1 week'
                      AND (
                          t.completed_at IS NULL
                          OR t.completed_at >= w.week_start + INTERVAL '1 week'
                      )
                ) AS overdue_tasks,

                -- overdue_percent reflects the percentage of overdue tasks among all tasks
                -- that existed by the end of the week
                ROUND(
                    CASE
                        WHEN COUNT(t.id) = 0 THEN 0
                        ELSE
                            COUNT(t.id) FILTER (
                                WHERE t.due_date IS NOT NULL
                                  AND t.due_date < w.week_start + INTERVAL '1 week'
                                  AND (
                                      t.completed_at IS NULL
                                      OR t.completed_at >= w.week_start + INTERVAL '1 week'
                                  )
                            ) * 100.0 / COUNT(t.id)
                    END,
                    2
                ) AS overdue_percent

            FROM weeks w
            LEFT JOIN tasks t
                ON t.user_id = :user_id
               AND t.created_at < w.week_start + INTERVAL '1 week'
            GROUP BY w.week_start
            ORDER BY w.week_start
        """)

        result = await db.execute(query, {"user_id": user_id})
        return [dict(row) for row in result.mappings().all()]
