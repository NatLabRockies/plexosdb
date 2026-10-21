SELECT tag.data_id, object.name, class.name, class.lang_id
FROM t_tag AS tag
JOIN t_object AS object ON tag.object_id = object.object_id
JOIN t_class AS class ON object.class_id = class.class_id
WHERE tag.action_id IS NOT NULL AND class.lang_id != ?
