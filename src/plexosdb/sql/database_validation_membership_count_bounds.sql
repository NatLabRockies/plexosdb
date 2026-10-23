WITH collection_limits AS (
    SELECT collection_id, name,
           CASE
               WHEN max_count = -1 THEN NULL
               WHEN max_count >= 0 THEN max_count
               WHEN COALESCE(is_one_to_many, 0) = 0 THEN 1
               ELSE NULL
           END AS max_allowed
    FROM t_collection
    WHERE max_count IS NOT NULL OR is_one_to_many = 0
)
SELECT limits.collection_id, limits.name, limits.max_allowed,
       membership.parent_object_id, COUNT(*)
FROM collection_limits AS limits
JOIN t_membership AS membership ON membership.collection_id = limits.collection_id
WHERE limits.max_allowed IS NOT NULL
GROUP BY limits.collection_id, membership.parent_object_id
HAVING COUNT(*) > limits.max_allowed
