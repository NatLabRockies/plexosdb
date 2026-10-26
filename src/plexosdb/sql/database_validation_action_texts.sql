SELECT text.data_id, class.name, class.lang_id
FROM t_text AS text
JOIN t_class AS class ON text.class_id = class.class_id
WHERE text.action_id IS NOT NULL AND class.lang_id != ?
