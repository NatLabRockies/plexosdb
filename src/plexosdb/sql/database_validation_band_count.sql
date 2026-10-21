SELECT property.property_id, property.name, property.max_band_id, MAX(band.band_id)
FROM t_band AS band
JOIN t_data AS data ON band.data_id = data.data_id
JOIN t_property AS property ON data.property_id = property.property_id
WHERE property.max_band_id IS NOT NULL
GROUP BY property.property_id
HAVING MAX(band.band_id) > property.max_band_id
