SELECT obj.object_id, obj.name, obj.class_id, category.class_id, category.name
FROM t_object AS obj
JOIN t_category AS category ON obj.category_id = category.category_id
WHERE obj.class_id != category.class_id
