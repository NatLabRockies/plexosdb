SELECT data.data_id, data.value, property.name, property.validation_rule
FROM t_data AS data
JOIN t_property AS property ON data.property_id = property.property_id
WHERE property.validation_rule IS NOT NULL AND property.validation_rule != ''
