WITH collisions AS (
    SELECT class_id, LOWER(name) AS lower_name
    FROM t_object
    GROUP BY class_id, LOWER(name)
    HAVING COUNT(*) > 1
)
SELECT object.class_id, collisions.lower_name,
       CASE WHEN class.class_id IS NULL THEN 'Unknown' ELSE class.name END,
       object.name, object.object_id
FROM collisions
JOIN t_object AS object
  ON object.class_id IS collisions.class_id
 AND LOWER(object.name) IS collisions.lower_name
LEFT JOIN t_class AS class ON object.class_id = class.class_id
ORDER BY object.class_id, collisions.lower_name, object.object_id
