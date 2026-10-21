SELECT data.data_id, property.name, property.collection_id, membership.collection_id
FROM t_data AS data
JOIN t_property AS property ON data.property_id = property.property_id
JOIN t_membership AS membership ON data.membership_id = membership.membership_id
WHERE property.collection_id != membership.collection_id
