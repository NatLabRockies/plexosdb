SELECT attribute.name, attribute.class_id, object.name, object.class_id
FROM t_attribute_data AS data
JOIN t_attribute AS attribute ON data.attribute_id = attribute.attribute_id
JOIN t_object AS object ON data.object_id = object.object_id
WHERE attribute.class_id != object.class_id
