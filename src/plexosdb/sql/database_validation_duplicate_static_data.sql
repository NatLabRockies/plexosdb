SELECT data.membership_id, data.property_id, COALESCE(band.band_id, 1), COUNT(*)
FROM t_data AS data
JOIN t_property AS property ON data.property_id = property.property_id
LEFT JOIN t_band AS band ON data.data_id = band.data_id
WHERE property.is_dynamic = 0
GROUP BY data.membership_id, data.property_id, COALESCE(band.band_id, 1)
HAVING COUNT(*) > 1
