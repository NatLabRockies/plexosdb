SELECT data.value, attribute.name, attribute.validation_rule, object.name
FROM t_attribute_data AS data
JOIN t_attribute AS attribute ON data.attribute_id = attribute.attribute_id
JOIN t_object AS object ON data.object_id = object.object_id
WHERE attribute.validation_rule IS NOT NULL AND attribute.validation_rule != ''
