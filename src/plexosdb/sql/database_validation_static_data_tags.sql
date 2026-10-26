SELECT tag.data_id, tag.object_id, tag.action_id
FROM t_tag AS tag
JOIN t_data AS data ON tag.data_id = data.data_id
JOIN t_property AS property ON data.property_id = property.property_id
WHERE property.is_dynamic = 0
