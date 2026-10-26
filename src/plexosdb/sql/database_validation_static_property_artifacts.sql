SELECT property.property_id, property.name, COUNT(*)
FROM $table AS artifact
JOIN t_data AS data ON artifact.data_id = data.data_id
JOIN t_property AS property ON data.property_id = property.property_id
WHERE property.is_dynamic = 0
  AND $artifact_filter
GROUP BY property.property_id
