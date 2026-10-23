SELECT data.data_id, data.membership_id, data.property_id, data.value,
       CASE WHEN band.data_id IS NULL THEN 1 ELSE band.band_id END,
       date_from.date, date_to.date, memo.value
FROM t_data AS data
LEFT JOIN t_band AS band ON data.data_id = band.data_id
LEFT JOIN t_date_from AS date_from ON data.data_id = date_from.data_id
LEFT JOIN t_date_to AS date_to ON data.data_id = date_to.data_id
LEFT JOIN t_memo_data AS memo ON data.data_id = memo.data_id
ORDER BY data.data_id
