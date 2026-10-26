SELECT data.data_id, data.membership_id, data.property_id, COALESCE(band.band_id, 1),
       property.name, object.name, object.object_id, class.name,
       date_from.date, date_to.date, memo.value
FROM t_data AS data
JOIN t_property AS property ON data.property_id = property.property_id
LEFT JOIN t_band AS band ON data.data_id = band.data_id
LEFT JOIN t_membership AS membership ON data.membership_id = membership.membership_id
LEFT JOIN t_object AS object ON membership.child_object_id = object.object_id
LEFT JOIN t_class AS class ON object.class_id = class.class_id
LEFT JOIN t_date_from AS date_from ON data.data_id = date_from.data_id
LEFT JOIN t_date_to AS date_to ON data.data_id = date_to.data_id
LEFT JOIN t_memo_data AS memo ON data.data_id = memo.data_id
WHERE property.is_dynamic = 0
ORDER BY data.data_id
