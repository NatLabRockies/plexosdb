SELECT child.data_id
FROM $table AS child
LEFT JOIN t_data AS data ON child.data_id = data.data_id
WHERE data.data_id IS NULL
ORDER BY child.data_id
