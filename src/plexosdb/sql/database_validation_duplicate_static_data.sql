SELECT data.membership_id, data.property_id, COALESCE(band.band_id, 1), COUNT(*),
       property.name, object.name, object.object_id, class.name
FROM t_data AS data
JOIN t_property AS property ON data.property_id = property.property_id
LEFT JOIN t_band AS band ON data.data_id = band.data_id
LEFT JOIN t_membership AS membership ON data.membership_id = membership.membership_id
LEFT JOIN t_object AS object ON membership.child_object_id = object.object_id
LEFT JOIN t_class AS class ON object.class_id = class.class_id
WHERE property.is_dynamic = 0
GROUP BY data.membership_id, data.property_id, COALESCE(band.band_id, 1)
HAVING COUNT(*) > 1
