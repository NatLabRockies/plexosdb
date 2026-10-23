SELECT object.name, object.class_id, custom_column.name, custom_column.class_id
FROM t_memo_object AS memo
JOIN t_custom_column AS custom_column ON memo.column_id = custom_column.column_id
JOIN t_object AS object ON memo.object_id = object.object_id
WHERE custom_column.class_id != object.class_id
