SELECT data.value, attribute.name, attribute.validation_rule, object.name, class.name
FROM t_attribute_data AS data
JOIN t_attribute AS attribute ON data.attribute_id = attribute.attribute_id
JOIN t_object AS object ON data.object_id = object.object_id
LEFT JOIN t_class AS class ON object.class_id = class.class_id
