SELECT text.data_id, text.class_id, text.value, text.action_id
FROM t_text AS text
JOIN t_data AS data ON text.data_id = data.data_id
JOIN t_property AS property ON data.property_id = property.property_id
WHERE property.is_dynamic = 0
